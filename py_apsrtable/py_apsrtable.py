from __future__ import division

class generateTable(object):
    
    def __init__(self, output, models, center='True', parens='se',
            sig_level=0.05, var_names=None):
        """
        Parameters
        ----------
        output : File to write the table to or 'print', string. If output ==
        'print' the table will be printed to the Python shell, else it will be
        written to the file specified.   

        models : Models to placed in the LaTeX table, list. This should be a
        list of pandas object generated by statsmodels.

        center : Whether the table should be centered or not, boolean. Defaults
        to 'True'

        parens : What values should be in the parentheses, string. Options are 
        'se' for standard errors, 'pval' for p values, and 'pval_one' for 
        one-tailed p values. Defaults to 'se'.

        sig_level : Indicates which values should be 'significant'. Integer.

        var_names : Strings to be used as variable names, list. Optional. 

        Note
        ----

        When replacing the variable names it is important to look at the sorted 
        ordering of the model (i.e. sorted(model.iteritems()) ) and order the
        list of replacement names accordingly. 

        """
        self.output = output
        self.models = models
        self.center = center
        self.parens = parens
        self.sig_level = sig_level
        self.var_names = var_names

    def create_model(self):
        """
        Takes the model to be placed in the table, turns it into a list, and 
        determines the number of models.

        Returns
        ------
        self.inputModel : A dict with each variable name as the key and a list
        of the beta values, standard errors, and p values for each model as the
        values. 

        """
        results = []
        for test_model in self.models:
            params = dict(test_model.params)
            bse = dict(test_model.bse)
            pvals = dict(test_model.pvalues)
            results.append(dict((k, [params[k], bse.get(k), pvals.get(k)]) for k in sorted(params.iterkeys())))
        tempModel = {}
        for key in results[0]:
            tempModel[key] = [results[0][key]]
        for model in results[1:len(results)]:
            for key in model:
                if key not in tempModel:
                    tempModel[key] = [['', '', '']]
        for i in range(1,len(results)):
            diff = set(tempModel) - set(results[i])
            for key in results[i]:
                tempModel[key].append(results[i][key])
            for key in diff:
                tempModel[key].append(['','',''])
        if self.var_names == None:
            self.inputModel = tempModel
        elif type(self.var_names) == list:
            replace = self.var_names
            newResults = []
            resultsList = sorted(tempModel.iteritems())
            for item in resultsList:
                newVar = list(item)
                newResults.append(newVar)
            for i in range(len(newResults)):
                newResults[i][0] = replace[i]
                self.inputModel = dict(newResults)

    def gen_table_body(self, stars, digits, stats):
        """
        Creates the columns that contain the models. Iterates through each 
        variable name and appends the values to the column if they exist, or an 
        empty column if the variable is not present in that certain model.

        Inputs
        ------

        stars : argument indicating whether stars should be included to indicate
        significance. Boolean
        """
        parens_position = {'se' : 1, 'pval' : 2, 'pval_one' : 2}
        text = ''
        for key in sorted(self.inputModel):
            text += str(key)
            for i in range(len(self.models)):
                beta = self.inputModel[key][i][0]
                if beta == '':
                    text += '  &   '
                else:
                    int(beta)
                    text += '   &   ' +  str(round(beta, digits))
            text += """  \\\\  
                    """
            for i in range(len(self.models)):
                if self.parens == 'pval_one':
                    parens = (self.inputModel[key][i][parens_position[self.parens]])/2
                else:
                    parens = self.inputModel[key][i][parens_position[self.parens]]
                if parens == '':
                    text += '  &   '
                else:
                    if stars == True:
                        if round(self.inputModel[key][i][2], digits
                                 ) <= self.sig_level:
                            int(parens)
                            text += ('   &   ' +  '(' + str(round(parens, digits
                                                                  )) + ')'
                            + '*')
                        elif round(self.inputModel[key][i][2], digits
                                   ) > self.sig_level:
                            int(parens)
                            text += '   &   ' +  '(' + str(round(parens, digits
                                                                 )) + ')'
                    elif stars == False:
                        int(parens)
                        text += '   &   ' +  '(' + str(round(parens, digits)) \
                                + ')'
            text += """  \\\\
                    """
#TODO: This implementation is messy and I don't like it, but it gets the idea
#down. These values need to be put into a list or dict and then iterate through
#it.
        # Account for inconsistent upper/lowercase:
        stats_uniform = [x.upper() for x in stats]
        available_stats = ['N', 'DF_MODEL', 'FVALUE', 'F_PVALUE', 'AIC',
                           'BIC', 'RSQUARED', 'RSQUARED_ADJ']
        # Stats asked for but not available:
        problems = [val for val in stats_uniform if val not in available_stats]
        if problems != []:
            raise Exception("Stat(s) " + ", ".join([str(x.upper()) for x in
                                              problems]) + " not available.")
        if "N" in stats_uniform:
            text += """
                        $N$ """
            for model in self.models:
                text += '    &    ' + str(model.nobs)
        if "DF_MODEL" in stats_uniform:
            text += """ \\\\
                        d.f. """
            for model in self.models:
                text += '    &    ' + str(model.df_model)
        if "FVALUE" in stats_uniform:
            text += """ \\\\
                        F-statistic """
            for model in self.models:
                text += '    &    ' + str(model.fvalue)
        if "F_PVALUE" in stats_uniform:
            text += """ \\\\
                        Model $p$ value """
            for model in self.models:
                text += '    &    ' + str(model.f_pvalue)
        if "AIC" in stats_uniform:
            text += """ \\\\
                        AIC """
            for model in self.models:
                text += '    &    ' + str(round(model.aic, 2))
        if "BIC" in stats_uniform:
            text += """ \\\\
                        BIC """
            for model in self.models:
                text += '    &    ' + str(round(model.bic))
        if "RSQUARED" in stats_uniform:
            text += """ \\\\
                        $R^{2}$ """
            for model in self.models:
                text += '    &    ' + str(round(model.rsquared))
        if "RSQUARED_ADJ" in stats_uniform:
            text += """ \\\\
                        $Adj.\>R^{2} $ """
            for model in self.models:
                text += '    &    ' + str(round(model.rsquared_adj))
        text += """ \\\\ \hline
                """
        return text            

    def start_table(self, caption, label, model_name=None):
        """
        Generates the top, or header, portion of a LaTeX table.

        Parameters
        ----------
        caption : The caption for the table (e.g. "OLS Results"), string. 

        label : The LaTeX label for the table (e.g. "tab:ols"), string. 

        model_name : Name of the model, list. Optional. If not included model
        names default to 'Model 1', 'Model 2', etc.

        Output
        ------
        Writes the header of the LaTeX table to the indicated file. 
        
        """
        self.model_number = len(self.models)
        tableSize = 'c '*(self.model_number)+'c'
        if model_name == None:
            name = []
            for i in range(1, len(self.models)+1):
                name.append('Model ' + str(i))
            if self.center == 'True':
                header = """
\\begin{table}
\caption{%s}
\center
\label{%s}
\\begin{center}
\\begin{tabular}{%s}
\hline\hline """ % (caption, label, tableSize)
                for label in name:
                    header += '  &     %s' % (label)
                header += """ \\\\
\hline
"""
            elif self.center == 'False':
                header = """
\\begin{table}
\caption{%s}
\label{%s}
\\begin{tabular}{%s}
\hline\hline """ % (caption, label, tableSize)
                for label in name:
                    header += '  &     %s' % (label)
                header += """ \\\\
\hline
"""
            else:
                print 'Please enter a valid string ("True" or "False") for the center argument'
            return header
        elif type(model_name) == list:
            name = model_name
            if self.center == 'True':
                header = """
\\begin{table}
\caption{%s}
\center
\label{%s}
\\begin{center}
\\begin{tabular}{%s}
\hline\hline """ % (caption, label, tableSize)
                for label in name:
                    header += '  &     %s' % (label)
                header += """ \\\\
\hline
"""
            elif self.center == 'False':
                header = """
\\begin{table}
\caption{%s}
\label{%s}
\\begin{tabular}{%s}
\hline\hline """ % (caption, label, tableSize)
                for label in name:
                    header += '  &     %s' % (label)
                header += """ \\\\
\hline
"""
            else:
                print 'Please enter a valid string ("True" or "False") for the center argument'
            return header
        else:
            print 'Please enter a valid list or string for model_name'

    def model_table(self, stars, digits, stats):
        """
        Generates the middle, which contains the actual model, of the LaTeX 
        table using the model generated in the createModel function.

        Input
        -----

        stars : Whether or not to include stars next the values in parentheses
        if the p value for that variable is less than .05, boolean. Defaults to
        True.

        Outputs
        -------
        Writes the middle of the LaTeX, which contains the actual model
        information, to the output file.
        
        """
        if type(self.inputModel) == dict:
            if stars == True:
                body = self.gen_table_body(stars, digits, stats)
                return body
            elif stars == False:
                body = self.gen_table_body(stars, digits, stats)
                return body
            else:
                print 'Please input a valid argument for the stars option'
        else:
            print 'Please input a dict object for the models'

                      
    def end_table(self):
        """
        Generates the bottom, or footer, portion of a LaTeX table.

        Output
        ------
        Writes the footer to the output table. 
        
        """
        tableSize = self.model_number + 1
        if self.center == 'True':
            if self.parens == 'se':
                footer = """
\hline
\multicolumn{%d}{l}{\\footnotesize{Standard Errors in parentheses}}\\\\
\multicolumn{%d}{l}{\\footnotesize{$^*$ indicates significance at $p \le$ %.2f}}
\end{tabular}
\end{center}
\end{table}
                """ % (tableSize, tableSize, self.sig_level)
            elif self.parens == 'pval':
                footer = """
\hline
\multicolumn{%d}{l}{\\footnotesize{$p$ values in parentheses}}\\\\
\multicolumn{%d}{l}{\\footnotesize{$^*$ indicates significance at $p \le$ %.2f}}
\end{tabular}
\end{center}
\end{table}
                """ % (tableSize, tableSize, self.sig_level)
            elif self.parens == 'pval_one':
                footer = """
\hline
\multicolumn{%d}{l}{\\footnotesize{One-tailed $p$ values in parentheses}}\\\\
\multicolumn{%d}{l}{\\footnotesize{$^*$ indicates significance at $p \le$ %.2f}}
\end{tabular}
\end{center}
\end{table}
                """ % (tableSize, tableSize, self.sig_level)
            else:
                print 'Please input a valid entry for the parens argument'
        elif self.center == 'False':
            footer = """
\hline
\multicolumn{%d}{l}{\\footnotesize{Standard Errors in parentheses}}\\\\
\multicolumn{%d}{l}{\\footnotesize{$^*$ indicates significance at $p \le$ %.2f}}
\end{tabular}
\end{table}
                """ % (tableSize, tableSize, self.sig_level)
        return footer

    def create_table(self, caption, label, model_name = None, stars=True,
                     digits = 2, stats = ['N']):
        """
        Combines all of the model-creation functions together into one easy to
        use function. 

        Inputs
        ------
        caption : The caption for the table (e.g. "OLS Results"), string. 

        label : The LaTeX label for the table (e.g. "tab:ols"), string. 

        model_name : Name of the model, list. Optional. If not included model
        names default to 'Model 1', 'Model 2', etc.

        stars : Whether or not to include stars next the values in parentheses
        if the p value for that variable is less than the specified significance
        level, boolean. Defaults to True.
        """
        self.create_model()
        header = self.start_table(caption, label, model_name=model_name)
        body = self.model_table(stars=stars, digits = digits, stats = stats)
        footer = self.end_table()
        table = header +  body + footer
        if self.output == 'print':
            print table
        else:
            outFile = open(self.output, 'w')
            outFile.write(table)
            outFile.close()
