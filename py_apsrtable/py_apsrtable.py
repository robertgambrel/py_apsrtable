class generateTable(object):
    
    def __init__(self, output, models, center='True', parens='se', var_names=None):
        """
        Parameters
        ----------
        output : File to write the table to, string.

        models : Models to placed in the LaTeX table, list. This should be a list of pandas object generated by statsmodels.

        center : Whether the table should be centered or not, boolean. Defaults to 'True'

        parens : What values should be in the parentheses, string. Options are 'se' for standard errors, 'pval' for p values, and 'pval_one' for one-tailed p values. Defaults to 'se'.

        var_names : Strings to be used as variable names, list. Optional. 

        Note
        ----

        When replacing the variable names it is important to look at the sorted ordering of the model (i.e. sorted(model.iteritems()) ) and order the list of replacement names accordingly. 

        """
        self.output = output
        self.models = models
        self.center = center
        self.parens = parens
        self.var_names = var_names

    def create_model(self):
        """
        Takes the model to be placed in the table, turns it into a list, and determines the number of models.

        Returns
        ------
        self.inputModel : A dict with each variable name as the key and a list of the beta values, standard errors, and p values for each model as the values. 

        """
        # Creates the temp holding list. What will be created is a list of dicts for each model.
        results = []
        # Iterate through each model in the self.models and get the relevent parameters. Append to results a dict with the key as the variable and the value as a list of the parameters. 
        for test_model in self.models:
            params = dict(test_model.params)
            bse = dict(test_model.bse)
            pvals = dict(test_model.pvalues)
            results.append(dict((k, [params[k], bse.get(k), pvals.get(k)]) for k in sorted(params.iterkeys())))
        #Temporary holding dict. This will be a dict that contains each variable as a key and the parameters for each of the three models as values. The structure is as follows:
        # {'var1': [['beta_model1', 'se_model1', 'pvalues_model1'], ['beta_model2', 'se_model2', 'pvalues_model2']], 'var2' : [['beta_model1', 'se_model1', 'pvalues_model1'], ['', '', '']]}
        tempModel = {}
        #Iterate through the keys in the first model and add the key and values from the first model to the tempModel.
        for key in results[0]:
            tempModel[key] = [results[0][key]]
        #Iterate through the rest of the models. If the variable in the model is not in the tempModel add the key with empty strings. This makes it to where tempModel contains all of the variables from every model.
        for model in results[1:len(results)]:
            for key in model:
                if key not in tempModel:
                    tempModel[key] = [['', '', '']]
        #Takes each model and gets the difference between it and the tempModel. This shows what variables are in model[i]. It then appends the values from model[i] to the variable in tempModel, and adds the empty strings to the variables that aren't in model[i].
        for i in range(1,len(results)):
            diff = set(tempModel) - set(results[i])
            for key in results[i]:
                tempModel[key].append(results[i][key])
            for key in diff:
                tempModel[key].append(['','',''])
        #This is changing the variable names. 
        #If the variable names aren't going to be changed, assign tempModel to self.inputModel.
        if self.var_names == None:
            self.inputModel = tempModel
        #If there are variable names and they are in a list sort the iteritems from tempModel and store them in resultsList. Iterate through resultsList and create a new list called newResults. Then replace the variable, which is stored in newResults[i][0] with the new variable name stored in replace[i]. Finally, assign the newResults to self.inputModel.
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

    def start_table(self, caption, label, model_name=None):
        """
        Generates the top, or header, portion of a LaTeX table.

        Parameters
        ----------
        caption : The caption for the table (e.g. "OLS Results"), string. 

        label : The LaTeX label for the table (e.g. "tab:ols"), string. 

        model_name : Name of the model, string. Optional. If not included model names default to 'Model 1', 'Model 2', etc.

        Output
        ------
        Writes the header of the LaTeX table to the indicated file. 
        
        """
        file = open(self.output, 'w')
        self.model_number = len(self.models)
        #Create the table size, which will be used to define the size of the LaTeX table.
        tableSize = 'c '*(self.model_number)+'c'
        #If there are no model names, create a list of model names ranging from 1 to the number of models.
        if model_name == None:
            name = []
            for i in range(1, len(self.models)+1):
                name.append('Model ' + str(i))
            #Create the header for center == 'True'
            if self.center == 'True':
                header = """
\\begin{table}
\caption{%s}
\center
\label{%s}
\\begin{center}
\\begin{tabular}{%s}
\hline\hline """ % (caption, label, tableSize)
                #Append the header with the model names and then append the LaTeX newline characters '\\'
                for label in name:
                    header += '  &     %s' % (label)
                header += """ \\\\
\hline
"""
            #Same as above except for center == 'False'
            elif self.center == 'False':
                header = """
\\begin{table}
\caption{%s}
\label{%s}
\\begin{tabular}{%s}
\hline\hline """ % (caption, label, tableSize)
                #Append the header with the model names and then append the LaTeX newline characters '\\'
                for label in name:
                    header += '  &     %s' % (label)
                header += """ \\\\
\hline
"""
            #Print out an exception if something funky is typed in for center
            else:
                print 'Please enter a valid string ("True" or "False") for the center argument'
            #Write the header and close the file
            file.write(header)
            file.close()
        #Sanity check to make sure there is an actual list with model names in it
        elif type(model_name) == list:
            #Assign name as the model_names given in the args
            name = model_name
            #Create header for the center == 'True' arg
            if self.center == 'True':
                header = """
\\begin{table}
\caption{%s}
\center
\label{%s}
\\begin{center}
\\begin{tabular}{%s}
\hline\hline """ % (caption, label, tableSize)
                #Append the header with the model names and then append the LaTeX newline characters '\\'
                for label in name:
                    header += '  &     %s' % (label)
                header += """ \\\\
\hline
"""
            #Same as above except for center == 'False'
            elif self.center == 'False':
                header = """
\\begin{table}
\caption{%s}
\label{%s}
\\begin{tabular}{%s}
\hline\hline """ % (caption, label, tableSize)
                #Append the header with the model names and then append the LaTeX newline characters '\\'
                for label in name:
                    header += '  &     %s' % (label)
                header += """ \\\\
\hline
"""
            #Print out an exception if something funky is typed in for center
            else:
                print 'Please enter a valid string ("True" or "False") for the center argument'
            #Write the header and close the file
            file.write(header)
            file.close()
        #If model_names isn't None or given a list of length >= 1 print out this error message
        else:
            print 'Please enter a valid list or string for model_name'


    def model_table(self, stars=True): 
        """
        Generates the middle, which contains the actual model, of the LaTeX table using the model generated in the createModel function.

        Input
        -----

        stars : Whether or not to include stars next the values in parentheses if the p value for that variable is less than .05, boolean. Defaults to True.

        Outputs
        -------
        Writes the middle of the LaTeX, which contains the actual model information, to the output file.
        
        """
        #TODO: Refactor the code to add another function that takes care of the looping so the code cleaner/more
        #compact
        #Sanity check to make sure a dict is getting passed and not something weird
        if type(self.inputModel) == dict:
            #The magic stars should be added.
            if stars == True:
                #Case where standard errors are placed in the parentheses.
                if self.parens == 'se':
                    file = open(self.output, 'a')
                    #Initialize the text variable that will be written to the table
                    text = ''
                    #Iterating through each key in the model 
                    for key in sorted(self.inputModel):
                        #Add the specific key (variable name) to the text
                        text += str(key)
                        #Iterating through the each of the models and adding the beta values (stored in inputModel[key][i][0]) to the text.
                        for i in range(len(self.models)):
                            beta = self.inputModel[key][i][0]
                            #If that model doesn't have any values for that particular variable append an empty column
                            if beta == '':
                                text += '  &   '
                            #If there is a value, append that value rounded to 2 decimal places
                            else:
                                int(beta)
                                text += '   &   ' +  str(round(beta,2))
                        #At the end of each key (variable) add the LaTeX newline character
                        text += """  \\\\  
                                """
                        #Doing the same procedure as above except for the values that should go in parentheses
                        for i in range(len(self.models)):
                            parens = self.inputModel[key][i][1]
                            if parens == '':
                                text += '  &   '
                            else:
                                #Checking the p values in order to add the magic stars
                                if round(self.inputModel[key][i][2],2) <= .05:
                                    int(parens)
                                    text += '   &   ' +  '(' + str(round(parens,2)) + ')' + '*'
                                elif round(self.inputModel[key][i][2],2) > .05:
                                    int(parens)
                                    text += '   &   ' +  '(' + str(round(parens,2)) + ')'
                        text += """  \\\\
                                """
                    #Write the model to the file and close the file
                    file.write(text)            
                    file.close()
                #Everything in this block is the same as the self.parens == 'se' except adding the pvalues to the parens instead of the standard errors
                elif self.parens == 'pval':
                    file = open(self.output, 'a')
                    text = ''
                    for key in sorted(self.inputModel):
                        text += str(key)
                        for i in range(len(self.models)):
                            beta = self.inputModel[key][i][0]
                            if beta == '':
                                text += '  &   '
                            else:
                                int(beta)
                                text += '   &   ' +  str(round(beta,2))
                        text += """  \\\\  
                                """
                        for i in range(len(self.models)):
                            parens = self.inputModel[key][i][2]
                            if parens == '':
                                text += '  &   '
                            else:
                                if round(self.inputModel[key][i][2],2) <= .05:
                                    int(parens)
                                    text += '   &   ' +  '(' + str(round(parens,2)) + ')' + '*'
                                elif round(self.inputModel[key][i][2],2) > .05:
                                    int(parens)
                                    text += '   &   ' +  '(' + str(round(parens,2)) + ')'
                        text += """  \\\\
                                """
                    file.write(text)            
                    file.close()
                #Everything the same here too, just adding one-tailed p values to the parens
                elif self.parens == 'pval_one':
                    file = open(self.output, 'a')                    
                    text = ''
                    for key in sorted(self.inputModel):
                        text += str(key)
                        for i in range(len(self.models)):
                            beta = self.inputModel[key][i][0]
                            if beta == '':
                                text += '  &   '
                            else:
                                int(beta)
                                text += '   &   ' +  str(round(beta,2))
                        text += """  \\\\  
                                """
                        for i in range(len(self.models)):
                            parens = (self.inputModel[key][i][2]/2.)
                            if parens == '':
                                text += '  &   '
                            else:
                                if round((self.inputModel[key][i][2]/2.),2) <= .05:
                                    int(parens)
                                    text += '   &   ' +  '(' + str(round(parens,2)) + ')' + '*'
                                elif round((self.inputModel[key][i][2]/2.),2) > .05:
                                    int(parens)
                                    text += '   &   ' +  '(' + str(round(parens,2)) + ')'
                        text += """  \\\\
                                """
                    file.write(text)            
                    file.close()
                #Print error message if the entry for parens isn't correct
                else:
                    print 'Please input a valid entry for the parens argument'
            #This is the section that takes care of the stars == False arg. Exact same as above except removed code to add stars. 
            elif stars == False:
                #Case where standard errors are placed in the parentheses.
                if self.parens == 'se':
                    file = open(self.output, 'a')
                    #Initialize the text variable that will be written to the table
                    text = ''
                    #Iterating through each key in the model 
                    for key in sorted(self.inputModel):
                        #Add the specific key (variable name) to the text
                        text += str(key)
                        #Iterating through the each of the models and adding the beta values (stored in inputModel[key][i][0]) to the text.
                        for i in range(len(self.models)):
                            beta = self.inputModel[key][i][0]
                            #If that model doesn't have any values for that particular variable append an empty column
                            if beta == '':
                                text += '  &   '
                            #If there is a value, append that value rounded to 2 decimal places
                            else:
                                int(beta)
                                text += '   &   ' +  str(round(beta,2))
                        #At the end of each key (variable) add the LaTeX newline character
                        text += """  \\\\  
                                """
                        #Doing the same procedure as above except for the values that should go in parentheses
                        for i in range(len(self.models)):
                            parens = self.inputModel[key][i][1]
                            if parens == '':
                                text += '  &   '
                            else:
                                int(parens)
                                text += '   &   ' +  '(' + str(round(parens,2)) + ')'
                        text += """  \\\\
                                """
                    #Write the model to the file and close the file
                    file.write(text)            
                    file.close()
                #Everything in this block is the same as the self.parens == 'se' except adding the pvalues to the parens instead of the standard errors
                elif self.parens == 'pval':
                    file = open(self.output, 'a')
                    text = ''
                    for key in sorted(self.inputModel):
                        text += str(key)
                        for i in range(len(self.models)):
                            beta = self.inputModel[key][i][0]
                            if beta == '':
                                text += '  &   '
                            else:
                                int(beta)
                                text += '   &   ' +  str(round(beta,2))
                        text += """  \\\\  
                                """
                        for i in range(len(self.models)):
                            parens = self.inputModel[key][i][2]
                            if parens == '':
                                text += '  &   '
                            else:
                                int(parens)
                                text += '   &   ' +  '(' + str(round(parens,2)) + ')'
                        text += """  \\\\
                                """
                    file.write(text)            
                    file.close()
                #Everything the same here too, just adding one-tailed p values to the parens
                elif self.parens == 'pval_one':
                    file = open(self.output, 'a')                    
                    text = ''
                    for key in sorted(self.inputModel):
                        text += str(key)
                        for i in range(len(self.models)):
                            beta = self.inputModel[key][i][0]
                            if beta == '':
                                text += '  &   '
                            else:
                                int(beta)
                                text += '   &   ' +  str(round(beta,2))
                        text += """  \\\\  
                                """
                        for i in range(len(self.models)):
                            parens = (self.inputModel[key][i][2]/2.)
                            if parens == '':
                                text += '  &   '
                            else:
                                int(parens)
                                text += '   &   ' +  '(' + str(round(parens,2)) + ')'
                        text += """  \\\\
                                """
                    file.write(text)            
                    file.close()
                #Print error message if the entry for parens isn't correct
                else:
                    print 'Please input a valid entry for the parens argument'
            else:
                print 'Please input a valid argument (True or false) for the stars option'
        #Print error message if the models aren't in a dict
        else:
            print 'Please input a dict object for the models'

                      
    def end_table(self):
        """
        Generates the bottom, or footer, portion of a LaTeX table.

        Output
        ------
        Writes the footer to the output table. 
        
        """
        #This one is all fairly self explanatory. Just create the footer based on what should be written in the comments. 
        file = open(self.output, 'a')
        tableSize = self.model_number + 1
        if self.center == 'True':
            if self.parens == 'se':
                footer = """
\hline
\multicolumn{%d}{l}{\\footnotesize{Standard Errors in parentheses}}\\\\
\multicolumn{%d}{l}{\\footnotesize{$^*$ indicates significance at $p \le$ 0.05 }} 
\end{tabular}
\end{center}
\end{table}
                """ % (tableSize, tableSize)
            elif self.parens == 'pval':
                footer = """
\hline
\multicolumn{%d}{l}{\\footnotesize{$p$ values in parentheses}}\\\\
\multicolumn{%d}{l}{\\footnotesize{$^*$ indicates significance at $p \le$ 0.05 }} 
\end{tabular}
\end{center}
\end{table}
                """ % (tableSize, tableSize)
            elif self.parens == 'pval_one':
                footer = """
\hline
\multicolumn{%d}{l}{\\footnotesize{One-tailed $p$ values in parentheses}}\\\\
\multicolumn{%d}{l}{\\footnotesize{$^*$ indicates significance at $p \le$ 0.05 }} 
\end{tabular}
\end{center}
\end{table}
                """ % (tableSize, tableSize)
            else:
                print 'Please input a valid entry for the parens argument'
        elif self.center == 'False':
            footer = """
\hline
\multicolumn{%d}{l}{\\footnotesize{Standard Errors in parentheses}}\\\\
\multicolumn{%d}{l}{\\footnotesize{$^*$ indicates significance at $p \le$ 0.05 }} 
\end{tabular}
\end{table}
                """ % (tableSize, tableSize)
        file.write(footer)
        file.close()

    



