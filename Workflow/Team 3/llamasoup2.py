import ollama
import pandas as pd
import time

fileN = 'GlassdoorPull-2024-11-25.csv'

df = pd.read_csv(fileN)
#print(df)

mod = 'llama3.1'

try:
    ollama.show(mod)
    print(f'{mod} found')
except:
    print(f'pulling model {mod}')
    ollama.pull(mod)

skills = df.T.loc['Description']

skilist = []

for s in skills.items():
    skilist.append(s[1])
    print(s[1])

index = 0
cont = 'y'

out = []

systemMes = 'Return a list of the skills required in the description provided in the previous message and format the output as a comma-separated list in curly-brackets like this: {a,b,c,d,e,...}.'
message2 = {'role': 'user','content': systemMes}

while index < len(skilist) and cont.startswith('y'):
    message1 = {'role':'user','content':skilist[index]}
    print('Sending response')
    response = ollama.chat(model=mod, messages=[message1,message2])
    print()
    res = response['message']['content']
    print(res)
    resCut = res.split('{')
    resCut = resCut[1].split('}')
    resCut = resCut[0]
    resCut = resCut.split(',')
    print(resCut)
    print()
    out.append(resCut)
    cont = input('continue? (y/n): ').lower()
    index += 1

dfOut = pd.DataFrame(out)

print(dfOut)

dfOut.to_csv(f'skillsOut{time.time()}.csv')