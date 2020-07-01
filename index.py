#pip3 install pandas
import pandas as pd

from ast import literal_eval

filename = "./articcle_text_authors.csv"
df = pd.read_csv(filename)


# This function serves to
# a) convert the "authors" col strings into Python-readable lists
# b) remove each author's first name
def lastname_producer(names):

    lastnames = []

    #turns stringified array into Python list
    try:
        fullname_array = literal_eval(names)
    except:
        return lastnames

    for fullname in fullname_array:
        #if there's a first and last name, append just the last name
        if " " in fullname:
            lastnames.append(fullname[fullname.rindex(" ")+1:])
        #if there's only one name, append that
        else:
            lastnames.append(fullname)

    return lastnames

#creates new column, "last_names"
#each row is populated w/ a list containing the last names of every author
#ex. [levendusky, pope, jackman]
df['last_names'] = df.apply(lambda row: lastname_producer(row['authors']), axis=1)

#a new row is created for each individual last name
# row index 0: [levendusky, pope, jackman]
# -->
# row index 0: [levendusky]
# row index 0: [pope]
# row index 0: [jackman]
df = df.explode("last_names")

# This function returns a truncated text.
# If the author's name appears in last 300 characters of a given text,
# then the sentence containing the author's name is removed.
# The sentences following the removed sentence are also removed.
def trunc_name(x):

    # Alter this variable if you want to expand how many characters are checked
    nbCharacters = 300

    if ((str(x['last_names'])) not in (x['text'][(-1 * nbCharacters):])):
        return x['text']

    else:
        #[-300:] selects last 300 characters of text.
        #        if string is less than or equal to 300 characters, it selects the whole string.
        #
        #.find   gets index of given word in last 300 characters
        index = x['text'][(-1 * nbCharacters):].find(str(x['last_names']))

        #if article has more than 300 characters, displace the index by the article's length
        if (len(x['text']) > nbCharacters):
            index += (len(x['text']) - nbCharacters)

        #substring from start of text to start of given word
        text = x['text'][0:index]

        #delete what remains between the previous sentence and the sentence in which the author's name appeared
        text = text.split('.')[:-1]

        #re-join
        text = '.'.join(text) + '.'

        return text

#applying the above function
df['trunc_text'] = df.apply(lambda row: trunc_name(row), axis=1)


#Debugging tool to determine which articles needed to be altered
#mask = ([ (str(a) in b[-300:]) for a,b in zip(df["last_names"], df["text"])])
#masktwo = ([ ("cknowledg" in b[-300:]) for b in df["text"]])
#print (df.loc[mask])

#-clean-up---
del df['last_names']

#merge identical rows
def shortest_agg(s):
    lst =  s.tolist()
    return sorted(lst, key = lambda x: len(x))[0]
df = df.groupby("file_name").agg(shortest_agg)
#------------

#Export to new CSV
df.to_csv('final.csv')
