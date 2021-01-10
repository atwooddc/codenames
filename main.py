
import requests as req

toGuess = ['trash', 'grouch', 'theater', 'screen', 'green']
toAvoid = ['whale', 'ear', 'keyboard', 'type', 'actor']
bystanders = ['tongue', 'mammal', 'poop']
assassin = ['potato']

def findbestclue(toGuess, toAvoid, bystanders, assassin):
    relatedWords = getRelatedWords(toGuess)
    updatedDict =  compareToWordsToAvoid(relatedWords, toAvoid)

def getRelatedWords() :
    relatedWords = {}
    for word in toGuess:
        url = 'http://api.conceptnet.io/query?node=/c/en/' + word
        resp = req.get(url).json()

        relatedToThis = {}
        i = 0

        while len(relatedToThis) < 20 and i < len(resp['edges']):
            start = resp['edges'][i]['start']
            end = resp['edges'][i]['end']
            if 'language' in start and 'language' in end:
                if start['language'] == 'en' and end['language'] == 'en' and '_' not in start['@id'] and '_' not in \
                        end['@id']:
                    if word not in end['label']:
                        related = end['label']
                    else:
                        related = start['label']
                    if ' ' in related:
                        related = removeArticlesandOtherWords(related)
                    if related not in word and word not in related:
                        relatedToThis[related.lower()] = round(resp['edges'][i]['weight'], 2)
            i += 1
        relatedWords[word] = relatedToThis
    print(relatedWords)
    return relatedWords

def removeArticlesandOtherWords(text):
    articles = {'a': '', 'an': '', 'and': '', 'the': ''}
    rest = []
    for word in text.split():
        if word not in articles:
            rest.append(word)
    # return last word - if there are any unecessary words that aren't articles, will likely be the first words
    return rest[-1]

# do I want to modify original dict or return a new one?
def compareToWordsToAvoid(wordsAndRelated, toAvoid, bystanders, assassin):
    updatedWordWeights = {}

    for word in wordsAndRelated:
        updatedWeights = {}
        for related in word:
            for compare in toAvoid :
                relatedness = findRelatedness(related, compare)
                if relatedness > 0.15:
                    updatedWeight = word[related] * (1 - relatedness)
            for compare in bystanders :
                relatedness = findRelatedness(related, compare)
                if relatedness > 0.15 :
                    updatedWeight = word[related] * (1 - 0.5*relatedness)
            relatedness = compare(related, assassin)
            if relatedness > 0.15 :
                updatedWeight = 0;
        updatedWordWeights[word] = updatedWeights
    return updatedWordWeights

def findRelatedness(w1, w2):
    url = 'http://api.conceptnet.io//relatedness?node1=/c/en/' + w1 + '&node2=/c/en/' + w2
    resp = req.get(url).json()
    return resp['value']

def findRelatednessTest() :
    print('these values should be HIGH')
    print('ball & racket: ' + findRelatedness('ball', 'racket'))
    print('butt & cheek: ' + findRelatedness('butt', 'cheek'))
    print('red & color' + findRelatedness('red', 'color'))
    print('trash & waste: ' + findRelatedness('trash','waste'))

    print('these values should be LOW')
    print('test & shirt: ' + findRelatedness('test', 'shirt'))
    print('round & lamp: ' + findRelatedness('round', 'lamp'))
    print('leap & soothe: ' + findRelatedness('leap', 'soothe'))
    print('candle & house: ' + findRelatedness('candle', 'house'))

    print('nuance test')
    print('halloween & holiday: ' + findRelatedness('halloween', 'holiday'))
    print('abacus & calculator: ' + findRelatedness('abacus', 'calculator'))
    print('sea & poseidon: ' + findRelatedness('sea', 'poseidon'))
    print('boy & girl: ' + findRelatedness('boy', 'girl'))

