import conditions as conditions
import numpy
import sys
import time

from scipy.optimize import linprog

def printTable(matrix):
    string = ""
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
          string = string + str(round((matrix[i][j]), 4)) + "      "
        print(string)
        string = ""


def calculateIndexes(matrix, minMax):
    shape = matrix.shape
    for i in range(2,shape[1]):
        value = 0
        valueM = 0
        if minMax == "min":
            for j in range(2, shape[0]-2):
                if matrix[j][0] < 999:
                    value = value + matrix[j][1]*matrix[j][i]
                else:
                    valueM = valueM + matrix[j][i]
        else:
            for j in range(2, shape[0]-2):
                if matrix[j][0] < 999:
                    value = value + matrix[j][1]*matrix[j][i]
                else:
                    valueM = valueM - matrix[j][i]
        if matrix[0][i] < 999:
            matrix[shape[0] - 2][i] = value - matrix[1][i]
            matrix[shape[0] - 1][i] = valueM
        else:
            matrix[shape[0] - 2][i] = value
            if minMax == "min":
                matrix[shape[0] - 1][i] = valueM - 1
            else:
                matrix[shape[0] - 1][i] = valueM + 1



def findIndexOfColumn(source):
    lineIsEmpty = True
    for i in range(3, source.shape[1]):

        if maxMin == "min" and source[-1][i] > 0:
            lineIsEmpty = False
            break
        if maxMin == "max" and source[-1][i] < 0:
            lineIsEmpty = False
            break

    if not lineIsEmpty:
        line = source[-1]
    else:
        line = source[source.shape[0] - 2]

    index = -1
    if maxMin == "min":
        value = -1
        for i in range(3, len(line) - 1):
            if line[i] > 0 and line[i] > value:
                value = line[i]
                index = i
    if maxMin == "max":
        value = 1
        for i in range(3, len(line) - 1):
            if line[i] < 0 and line[i] < value:
                value = line[i]
                index = i
    if index == -1:
        return 0
    return index

def findIndexOfLine(source, index):
    indexes = []
    for i in range(2, source.shape[0] - 2):
        if source[i][index] > 0:
            source[i][-1] = source[i][2] / source[i][index]
            indexes.append(i)

    if len(indexes) == 0:

        sys.exit("Целевая функция не ограничена")

    bestLine = indexes[0]
    for i in range(1, len(indexes)):
        if source[indexes[i]][-1] < source[bestLine][-1]:
            bestLine = indexes[i]
    return bestLine


def calculateColumn(matrix, columnIndex):
    for i in range(2, matrix.shape[0] - 2):
        if matrix[i][columnIndex] > 0:
            matrix[i][-1] = matrix[i][2]/matrix[i][columnIndex]
    return matrix

maxMin = "min"  # 3 вариант
objectiveFunction = "3*x1+4*x2+1*x3"
numberOfConditions = 3
conditions.append("-3*x1+1*x2+4*x3=7")
conditions.append("1*x1-1*x2-2*x3<=3")
conditions.append("2*x1+2*x2+4*x3>=0")


##### Определяем количество переменных ##########
variables = []
if "=" in conditions[0]:
    sep = "="
if "<=" in conditions[0]:
    sep = "<="
if ">=" in conditions[0]:
    sep = ">="

s = conditions[0].split(sep)
vars = s[0].split("*x")
for i in range(1, len(vars)):
    if "+" in vars[i]:
        sep = "+"
    if "-" in vars[i]:
        sep = "-"
    variables.append(vars[i].split(sep)[0])
###################################################

### Запись коэффициентов в целевой функции ##########
koefsInObjective = []
subStr = objectiveFunction
for i in range(len(variables)):
    splitedStr = subStr.split("*x" + str(variables[i]))
    subStr = splitedStr[1]
    koefsInObjective.append(float(splitedStr[0]))
#####################################################

#### Создаём матрицу коэффициентов ########
unsortedKoefs = [[] for _ in range(numberOfConditions)]
for i in range(numberOfConditions):
    for j in range(len(variables)):
        unsortedKoefs[i].append(0)
##############################################


####### Заполняем матрицу коэффициентов и свободных членов #########
freeElements = []
separators = []
for i in range(0, len(conditions)):
    if "=" in conditions[i]:
        sep = "="
    if "<=" in conditions[i]:
        sep = "<="
    if ">=" in conditions[i]:
        sep = ">="
    separators.append(sep)
    s = conditions[i].split(sep)
    vars = s[0].split("*x")
    freeElements.append(float(s[1]))
    for j in range(0, len(vars)-1):
        if j == 0:
            unsortedKoefs[i][j] = float(vars[j])
        else:
            if "+" in vars[j]:
                splitted = vars[j].split("+")
                unsortedKoefs[i][j] = float(splitted[1])
            else:
                splitted = vars[j].split("-")
                unsortedKoefs[i][j] = (-1) * float(splitted[1])
#######################################################


######## Если один из свободных коэффициентов отрицательный, то программа выдаст ошибку ########
for i in range(len(freeElements)):
    if freeElements[i] < 0:
        sys.exit("Один из свободных коэффициентов отрицательный, проверьте систему ограничений")

#################################################################################################



### Если уравнений несколько, то складываем коэффициенты ####
numberOfEquations = 0
for i in range(len(separators)):
    if separators[i] == "=":
        numberOfEquations = numberOfEquations + 1


################################################################################################################


print("Коэффициенты " + str(unsortedKoefs))

######### Определяем базисные переменные для уравнения #####################
source = numpy.zeros((numberOfConditions+4, len(variables)+3))
initialBaseline = []
basisVars = []
allVariables = []

for i in range(len(initialBaseline), len(variables)):
    initialBaseline.append(0)

for i in range(len(variables)):
    allVariables.append(variables[i])

for i in range(numberOfConditions):
    for j in range(len(variables)):
        source[i+2][j+3] = unsortedKoefs[i][j]
for i in range(len(variables)):
    source[0][i+3] = float(variables[i])
for i in range(len(variables)):
    source[1][i+3] = koefsInObjective[i]

### Если все коэффициенты уравнения отрицательные, а свободный член положительный, то значит система ограничений несовместна
if numberOfEquations > 0:
    for j in range(numberOfEquations):
        allNegative = True
        for i in range(len(unsortedKoefs[0])):
            if unsortedKoefs[j][i] > 0:
                allNegative = False
        if  allNegative == True and freeElements[0] > 0:
            sys.exit("Несовместная система ограничений, проверьте уравнения")


if numberOfEquations > 0:
    for i in range(numberOfEquations):
        value = 0
        value = float(allVariables[-1]) + 1
        if value > 999:
            value = value -1000

        allVariables.append(value)
        initialBaseline.append(0)
        column = numpy.zeros((numberOfConditions + 4, 1))
        column[0][0] = value
        column[2+i][0] = -1
        source = numpy.append(source, column, axis=1)

        allVariables.append(value + 1000)
        basisVars.append(value + 1000)
        source[2+i][0] = value+1000
        source[2+i][2] = freeElements[0+i]
        column = numpy.zeros((numberOfConditions + 4, 1))
        column[0][0] = value + 1000
        column[2+i][0] = 1
        source = numpy.append(source, column, axis=1)



for i in range(0,numberOfConditions):
    if separators[i] == "<=":
        value = 0
        for j in range(len(variables)):
            value = value + unsortedKoefs[i][j] * initialBaseline[j]
        initialBaseline.append(freeElements[i] - value)
        source[i+2][2] = freeElements[i] - value
        if float(allVariables[-1]) > 1000:
            value = float(allVariables[-1]) - 1000 + 1
        else:
            value = float(allVariables[-1]) + 1
        allVariables.append(value)
        source[i+2][0] = value
        basisVars.append(len(allVariables))
        column = numpy.zeros((numberOfConditions+4,1))
        column[0][0] = value
        column[i+2][0] = 1
        source = numpy.append(source, column, axis = 1)

    if separators[i] == ">=":

        if float(allVariables[-1]) > 1000:
            value = float(allVariables[-1]) - 1000 + 1
        else:
            value = float(allVariables[-1]) + 1
        allVariables.append(value)
        initialBaseline.append(0)
        column = numpy.zeros((numberOfConditions + 4, 1))
        column[0][0] = value
        column[i + 2][0] = -1
        source = numpy.append(source, column, axis=1)

        allVariables.append(value+1000)
        basisVars.append(value+1000)
        source[i+2][0] = value+1000
        column = numpy.zeros((numberOfConditions + 4, 1))
        column[0][0] = value+1000
        column[i + 2][0] = 1
        source = numpy.append(source, column, axis=1)

        value = 0
        for j in range(len(variables)):
            value = value + unsortedKoefs[i][j] * initialBaseline[j]
        initialBaseline.append(freeElements[i] - value)
        source[i+2][2] = freeElements[i] - value


column = numpy.zeros((numberOfConditions+4,1))
source = numpy.append(source, column, axis = 1)


print("Коэффициенты целевой функции " + str(koefsInObjective))
print("Переменные " + str(variables))
print("Коэффициенты " + str(unsortedKoefs))
print("Свободные члены " + str(freeElements))
print("Знаки " + str(separators))
print("Все переменные " + str(allVariables))
print("Начальный опорный план " + str(initialBaseline))
print("Базисные переменные " + str(basisVars))

iteration = 0
while True:
    print("\n\nИтерация " + str(iteration))
    calculateIndexes(source, maxMin)

    printTable(source)
    time.sleep(1)

    indexOfColumn = findIndexOfColumn(source)
    print("Конец если 0 " + str(indexOfColumn))
    if indexOfColumn == 0:
        endVariables = []

        for i in range(2, source.shape[0]-2):
            endVariables.append(source[i][0])
            if source[i][0] > 999:
                if source[i][2] != 0:
                    sys.exit("Система ограничений несовместна, не все искуственные переменные равны нулю")
        for i in range(3, source.shape[1]-1):
            if source[0][i] not in endVariables:
                if source[-1][i] != 0 and source[source.shape[0]-2][i] != 0:
                    sys.exit("Бесконечное множество оптимальных планов, не все свободные переменные имеют ноль в индексной строке")
        break

    indexOfLine = findIndexOfLine(source, indexOfColumn)
    print("Таблица")
    printTable(source)
    print("Определяющий столбец " + str(indexOfColumn))
    print("Определяющая строка " + str(indexOfLine))

    ### Определяю является ли омега - переменной в решающей строке, если да, то определяю индекс колонки, в которой записана омега для последующего удаления
    ind = 0
    if source[indexOfLine][0] > 999:
        for j in range(3, source.shape[1]):
            if source[0][j] == source[indexOfLine][0]:
                ind = j


    #  Заполнить таблицу
    source1 = numpy.zeros((source.shape[0], source.shape[1]))
    ### Заполнение первых двух строк (индекс переменной и коэффициент в целевой функции)
    for i in range(2):
        for j in range(source.shape[1]):
            source1[i][j] = source[i][j]
    ### Заполнение столбцов Cб и А0
    for i in range(2, source.shape[0]-2):
        if i == indexOfLine:
            source1[i][0] = source[0][indexOfColumn]
            source1[i][1] = source [1][indexOfColumn]
        else:
            source1[i][0] = source[i][0]
            source1[i][1] = source[i][1]
    ### Заполнение новой рабочей области таблицы
    for i in range(2, source.shape[0]-2):
        for j in range(2, source.shape[1]-1):
            if i == indexOfLine:
                source1[i][j] = source[i][j] / source[indexOfLine][indexOfColumn]
            else:
                if j == indexOfColumn and i != indexOfLine:
                    source1[i][j] = 0
                else:
                    source1[i][j] = (source[i][j]*source[indexOfLine][indexOfColumn]-source[i][indexOfColumn]*source[indexOfLine][j])/source[indexOfLine][indexOfColumn]
    ### Переопределение новой таблицы
    source = source1
    iteration = iteration + 1
    ### Удаление столбца с омега, если омега - оказалась в решающей строке на данной итерации
    if ind != 0:
        source = numpy.delete(source, ind, 1)


