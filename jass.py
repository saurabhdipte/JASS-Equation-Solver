import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('tagsets')
nltk.download('brown')
nltk.download('universal_tagset')
nltk.download('nps_chat')
nltk.download('treebank')


from nltk.tokenize import word_tokenize
import re

def question_input():
  user_input = input("Enter your question :")
  return(user_input)
  
metrics = {
"distance": ["km", "m", "cm", "kilometers", "meters", "centimeters", "kms"],
"time": ["hours", "hour", "minute", "minutes", "seconds", "second", "s","sec"],
"velocity": ["km/hr", "m/s","m/sec", "km/h", "kmph"],
"acceleration": ["m/s2", "m/s^2","m/sec2"]
}

def jassequationsolver():
  user_input_1 = question_input()
  problem_statement = user_input_1
  final_variable_to_find = Determining_Unknown_Variable(problem_statement)
  given, variables, variables_units = Determining_known_variable(problem_statement,final_variable_to_find) 
  variables_converted = ConvertToMKS(given, variables, variables_units)
  KinematicEquationSolver(final_variable_to_find, given, variables_converted)

def Determining_Unknown_Variable(problem):
  problem_statement_split = problem.split('.')
  question_words_list = [ 'Find','What', 'How much', 'Determine','How long','How far', 'How fast', 'Calculate' ]
  to_find_variable = ''
  question_word_found = ''
  i_location = 0

  for i in range(len(problem_statement_split)):
    for j in range(len(question_words_list)):
      if question_words_list[j].lower() in problem_statement_split[i].lower():
        to_find_variable = problem_statement_split[i]
        question_word_found = question_words_list[j].lower()
    tokens_to_find_variable = nltk.word_tokenize(to_find_variable)

  question_word_position = 0
  for i in range(len(tokens_to_find_variable)):
    if tokens_to_find_variable[i].lower() == question_word_found:
      question_word_position = i
    
  quantities_dict = {0: ['final velocity','velocity','final speed'],1:['initial velocity','initial speed'],2:['acceleration'],3:['time'],4:['displacement','distance']}
  q_tofindvar = ['final velocity','initial velocity','acceleration','time','displacement']
  q_tofind =[False,False,False,False,False]
  how_much_var = ''
  run_once = 0

  for p in range(question_word_position,len(tokens_to_find_variable)):
    w = tokens_to_find_variable[p]
    for i in range(len(quantities_dict)):
      l1 = quantities_dict[i]
      if question_word_found == 'how much':
        for k in range(len(tokens_to_find_variable)):
          if tokens_to_find_variable[k].lower() == 'how':
            how_much_var = tokens_to_find_variable[k+2]
          if how_much_var == 'time':
            q_tofind[3] = True
            i_loc = 3
          elif how_much_var == 'distance':
            q_tofind[4] = True
            i_loc = 4

      elif question_word_found == 'how long':
        q_tofind[3] = True
        i_loc = 3

      elif question_word_found == 'how far':
        q_tofind[4] = True  
        i_loc = 4

      elif question_word_found == 'how fast':
        q_tofind[0] = True 
        i_loc = 0

      else:
        for i in range(len(quantities_dict)):
          l1 = quantities_dict[i]
          for j in range(len(l1)):
            if run_once == 0:
              if l1[j] =='initial velocity' and w == 'initial':
                if tokens_to_find_variable[p+1] == 'velocity':
                  q_tofind[i] = True
                  i_loc = i
                  run_once = 1

              if l1[j] == w:
                q_tofind[i] = True
                i_loc = i
                run_once = 1
  
  print('The unknown quantity is: ', q_tofindvar[i_loc])   
  print('\n')   
  return (q_tofind)



def Determining_known_variable(problem, q_tofind):
  tokens = nltk.word_tokenize(problem)
  tagged = nltk.pos_tag(tokens)
  givenvar = ['Final velocity','initial velocity','acceleration','time','displacement']

  flag_rest = 0
  flag_stop = 0
  #[v, v0, a, t, x]
  variables = [0, 0, 0, 0, 0]
  variables_units = ['','','','','']
  given = [False, False, False, False, False]
  for i in range(len(tagged) - 1):
    if (tagged[i][0]) == "rest":
      if (tagged[i-1][0] == "at" or tagged[i-1][0] == "from"):
        variables[1] = 0.0
        given[1] = True
        flag_rest = 1

    if (tagged[i][0]) == "stop" or (tagged[i][0]) == "stops":
      variables[0] = 0.0
      given[0] = True
      flag_stop = 1

  for i in range(len(tagged) - 1):
    if (tagged[i][1] == "CD"):
      if ((tokens[i + 1] in metrics['velocity']) and (tokens[i - 1] == "from")):
        variables[1] = float(tokens[i])
        variables_units[1] = tokens[i+1]
        given[1] = True 
        
      if ((tokens[i + 1] in metrics['velocity']) and (tokens[i - 1] == "to")):
        variables[0] = float(tokens[i])
        variables_units[0] = tokens[i+1]
        given[0] = True

      if (q_tofind[0] == True and (tokens[i + 1] in metrics['velocity'])):
        variables[1] = float(tokens[i])
        variables_units[1] = tokens[i+1]
        given[1] = True         

      if (q_tofind[1] == True and (tokens[i + 1] in metrics['velocity'])):
        variables[0] = float(tokens[i])
        variables_units[0] = tokens[i+1]
        given[0] = True


      if (tokens[i + 1] in metrics['velocity']) and flag_rest == 1: #Additional check required if it is initial or final velocity
        variables[0] = float(tokens[i])
        variables_units[0] = tokens[i+1]
        given[0] = True

      if (tokens[i + 1] in metrics['velocity']) and flag_stop == 1: #Additional check required if it is initial or final velocity
        variables[1] = float(tokens[i])
        variables_units[1] = tokens[i+1]
        given[1] = True

      if (tokens[i + 1] in metrics['time']):
        variables[3] = float(tokens[i])
        variables_units[3] = tokens[i+1]
        given[3] = True

      if (tokens[i + 1] in metrics['acceleration']):
        if (tagged[i-1][1] == '$' or 'decelerates' in tokens or 'decelerate' in tokens or 'deceleration' in tokens):
          variables[2] = float(tokens[i]) * (-1)
        else:
          variables[2] = float(tokens[i])
        variables_units[2] = tokens[i+1]
        given[2] = True

      if (tokens[i + 1] in metrics['distance']):
        variables[4] = float(tokens[i])
        variables_units[4] = tokens[i+1]
        given[4] = True

  print('The known quantities are: ')
  for i in range(len(given)):
    if given[i] == True:
      print(givenvar[i],':',variables[i], variables_units[i])
  print('\n')

  return (given, variables, variables_units)


def ConvertToMKS(given, variables, variables_units):

  speed_kmph = ['kmph','km/hr','km/h']
  acc_kmphsq = ['km/h2','km/hr^2','km/h^2']
  time_hr = ['h','hr','hour','hours']
  dist_km = ['km','kilometer','kilometers']
  givenvar = ['final velocity','initial velocity','acceleration','time','displacement']
  MKSUnits = ['m/s','m/s','m/s^2','s','m']
  variables_converted = variables

  if variables_units[0] in speed_kmph:
    variables_converted[0] = round(variables[0] * 0.277778,3)
  else:
    variables_converted[0] = variables[0]

  if variables_units[1] in speed_kmph:
    variables_converted[1] = round(variables[1] * 0.277778, 3)
  else:
    variables_converted[1] = variables[1]

  if variables_units[2] in acc_kmphsq:
    variables_converted[2] = round(variables[2] * (1/12960),3)
  else:
    variables_converted[2] = variables[2]

  if variables_units[3] in time_hr:
    variables_converted[3] = round(variables[3] * 3600, 3)
  else:
    variables_converted[3] = variables[3]

  if variables_units[4] in dist_km:
    variables_converted[4] = round(variables[4] * 1000, 3)
  else:
    variables_converted[4] = variables[4]
  
  print('The known quantities after converting to MKS Units are: ')
  for i in range(len(given)):
    if given[i] == True:
      print(givenvar[i],':',variables_converted[i], MKSUnits[i])
  print('\n')

  return (variables_converted)


def KinematicEquationSolver(q_tofind, given, variables_converted):
  MKSUnits = ['m/s','m/s','m/s^2','s','m']

  if q_tofind[0] == True and ((given[1] == True) and (given[2] == True) and (given[3] == True)):
    print(equation1(variables_converted[1], variables_converted[2], variables_converted[3]), MKSUnits[0])
  if q_tofind[1] == True and ((given[0] == True) and (given[2] == True) and (given[3] == True)):
    print(equation2(variables_converted[0], variables_converted[2], variables_converted[3]), MKSUnits[1])
  if q_tofind[2] == True and ((given[0] == True) and (given[1] == True) and (given[3] == True)):
    print(equation3(variables_converted[0], variables_converted[1], variables_converted[3]), MKSUnits[2])
  if q_tofind[3] == True and ((given[0] == True) and (given[1] == True) and (given[2] == True)):
    print(equation4(variables_converted[0], variables_converted[1], variables_converted[2]), MKSUnits[3])
  if q_tofind[4] == True and ((given[1] == True) and (given[3] == True) and (given[2] == True)):
    print(equation5(variables_converted[1], variables_converted[3], variables_converted[2]), MKSUnits[4])
  if q_tofind[1] == True and ((given[4] == True) and (given[1] == True) and (given[2] == True)):
    print(equation6(variables_converted[4], variables_converted[1], variables_converted[2]), MKSUnits[1])
  if q_tofind[3] == True and ((given[4] == True) and (given[1] == True) and (given[2] == True)):
    print(equation7(variables_converted[4], variables_converted[1], variables_converted[2]), MKSUnits[3])
  if q_tofind[2] == True and ((given[4] == True) and (given[1] == True) and (given[3] == True)):
    print(equation8(variables_converted[4], variables_converted[1], variables_converted[3]), MKSUnits[2])
  if q_tofind[0] == True and ((given[1] == True) and (given[2] == True) and (given[4] == True)):
    print(equation9(variables_converted[1], variables_converted[2], variables_converted[4]), MKSUnits[0])
  if q_tofind[1] == True and ((given[0] == True) and (given[2] == True) and (given[4] == True)):
    print(equation10(variables_converted[0], variables_converted[2], variables_converted[4]), MKSUnits[1])
  if q_tofind[2] == True and ((given[0] == True) and (given[1] == True) and (given[4] == True)):
    print(equation11(variables_converted[0], variables_converted[1], variables_converted[4]), MKSUnits[2])
  if q_tofind[4] == True and ((given[0] == True) and (given[1] == True) and (given[2] == True)):
    print(equation12(variables_converted[0], variables_converted[1], variables_converted[2]), MKSUnits[4])
  if q_tofind[4] == True and ((given[0] == True) and (given[1] == True) and (given[3] == True)):
    a = equation3(variables_converted[0], variables_converted[1],variables_converted[3])
    print('Intermediate Equation')
    print('a =',a,'m/s^2')
    print('\n')
    print(equation12(variables_converted[0], variables_converted[1],a), MKSUnits[4])




def equation1(v0, a, t):
  v = v0 + (a * t)
  print('Equation Used: v = v0 + (a * t) ')
  return round(v,3)

def equation2(v, a, t):
  v0 = v - (a * t)
  print('Equation Used: v = v0 + (a * t) ')
  return round(v0,3)

def equation3(v, v0, t):
  a = (v - v0) / t
  print('Equation Used: v = v0 + (a * t) ')
  return round(a,3)


def equation4(v, v0, a):
  t = (v - v0) / a
  print('Equation Used: v = v0 + (a * t) ')
  return round(t,3)

def equation5(v0, t, a):
  if a > 0:
    x = (v0 * t) + ((1 / 2) * a * (t ** 2))
  else:
    x = (v0 * t) - ((1 / 2) * a * (t ** 2))

  print('Equation Used: x = (v0 * t) + ((1 / 2) * a * (t ** 2)) ')
  return round(x,3)

def equation6(x, t, a):
  v0 = (x - ((1 / 2) * a * (t ** 2))) / t
  print('Equation Used: x = (v0 * t) + ((1 / 2) * a * (t ^ 2)) ')
  return round(v0,3)

def equation7(x, v0, a):
  t = [(-v0 - (((v0 ** 2) - (4 * ((1 / 2) * a) * -x)) ** (1 / 2))) / (2 * ((1 / 2) * a)), (-v0 - (((v0 ** 2) - (4 * ((1 / 2) * a) * -x)) ** (1 / 2))) / (2 * ((1 / 2) * a))]
  print('Equation Used: x = (v0 * t) + ((1 / 2) * a * (t ^ 2)) ')
  return t

def equation8(x, v0, t):
  a = (x - (v0 * t)) / ((1 / 2) * (t ** 2))
  print('Equation Used: x = (v0 * t) + ((1 / 2) * a * (t ^ 2)) ')
  return round(a,3)

def equation9(v0, a, x):
  v = ((v0 ** 2) + (2 * a * x)) ** (1 / 2)
  print('Equation Used: v^2 = ((v0 ^ 2) + (2 * a * x)) ')
  return round(v,3)

def equation10(v, a, x):
  v0 = ((v ** 2) - (2 * a * x)) ** (1 / 2)
  print('Equation Used: v^2 = ((v0 ^ 2) + (2 * a * x)) ')
  return round(v0,3)

def equation11(v, v0, x):
  a = ((v ** 2) - (v0 ** 2)) / (2 * x)
  print('Equation Used: v^2 = ((v0 ^ 2) + (2 * a * x)) ')
  return round(a,3)

def equation12(v, v0, a):
  x = ((v ** 2) - (v0 ** 2)) / (2 * a)
  print('Equation Used: v^2 = ((v0 ^ 2) + (2 * a * x)) ')
  return round(x,3)


jassequationsolver()