import regex
import pandas as pd
import numpy as np
import emoji
from collections import Counter
import matplotlib.pyplot as plt
from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import re
from matplotlib.gridspec import GridSpec
import seaborn as sns
# import matplotlib.font_manager
from textblob import TextBlob
import os
import warnings
warnings.filterwarnings("ignore")

basedir = os.path.abspath(os.path.dirname(__file__))

from matplotlib.font_manager import FontProperties
prop = FontProperties(fname='/System/Library/Fonts/Apple Color Emoji.ttc')
plt.rcParams['font.family'] = prop.get_family()
# plt.rcParams['font.family'] = 'sans-serif'
# plt.rcParams['font.sans-serif'] = 'Helvetica'
plt.rcParams['axes.edgecolor']='#333F4B'
plt.rcParams['axes.linewidth']=0.8
plt.rcParams['xtick.color']='#333F4B'
plt.rcParams['ytick.color']='#333F4B'

colorlist = ["#D8DDEC","#D4EBD4","#EFEED8","#F9DFE1","#F6D0E8","#DFF2FD","#E2FCE6","#FCFADE","#FFEEE2","#FFDBDB","#F692BC","#F4ADC6","#FDFD95","#AAC5E2","#6891C3","#77DD77"]

path = basedir+"/temp/"

# filepath = input("Please Enter the Whatsapp chat export path below ")
# filepath = ("chat.txt")
def details(filepath):
    # filepath = "/" +filepath.split('/',2)[2]
    # print("data base ---", basedir)
    filepath = basedir + "/"+filepath
    # print("l------",filepath)
    # print("data",os.getcwd()) 
    df = pd.read_csv(filepath, sep = "delimiter",skip_blank_lines = True, header = None, engine='python')

    # extract date values and return as list of string
    def getdate(x):
        res = re.search("\d\d/\d\d/\d\d",x)
        if res != None:
            return res.group()
        else:
            return ""
    #datepattern = re.compile("../../..")
    df["Date"] = list(map(lambda x : getdate(x), df.iloc[:,0]))


    ## Merge multiline chat data
    ## Need to optimize this block
    for i in range(0,len(df)):
        if df["Date"][i] == "":
            c=i-1
            for j in range(i,len(df)):
                if df["Date"][j] == "":
                    df.iloc[c,0] = " ".join([df.iloc[c,0],df.iloc[j,0]])
                        
                else:
                    i=j-1
                    break
        else:
            df.iloc[i,0] = df.iloc[i,0]

        
    ## Remove rows where date is empty
    df.drop(np.where(df.iloc[:,1]=="")[0],inplace =True)
    ## Reindex the dataframe
    df.index = range(0,len(df))

    ##Remove date from original text data using substitute function of regular expression
    df.iloc[:,0] = list(map(lambda x : re.sub("../../..","", x)[2:],df.iloc[:,0]))



    ## Extract Day Month and Year from Date 
    df["Day"] = list(map(lambda d : d.split("/")[0], df.Date))
    df["Months"] = list(map(lambda d : d.split("/")[1], df.Date))
    df["Year"] = list(map(lambda d : d.split("/")[2], df.Date))

    ## extract time stamp from chat data and store in new column Time and Am
    def gettime(x):
        res = re.search(".*\d:\d\d\s[a|p]m", x)
        if res != None:
            return res.group()
        else:
            return ""
    Timestamp = list(map(lambda x : gettime(x),df.iloc[:,0])) 


    df["Time"] = list(map(lambda t : t.split(" ")[0],Timestamp))
    df["Hour"] = list(map(int,list(map(lambda t : t.split(":")[0],df["Time"]))))
    df["Minute"] = list(map(int,list(map(lambda t : t.split(":")[1],df["Time"]))))
    df["AmPm"] = list(map(lambda t : t.split(" ")[1],Timestamp))

    ## Remove Timestamps from chat
    df.iloc[:,0] = list(map(lambda x : re.sub(".*\d:\d\d\s[a|p]m","", x)[2:],df.iloc[:,0]))

    ## get sender
    def getsender(x):
        res = re.search(re.compile(".*?: "),x)
        if res !=None:
            return res.group()[1:-2]
        else:
            return ""
        
        
    df["sender"] =list(map(getsender,df.iloc[:,0]))


    ## Drop rows of activity messages - member added/removed/left/group name change/icon change/others
    df.drop((np.where(df["sender"]=="")[0]),inplace = True)
    ## Reindex the dataframe
    df.index = range(0,len(df))

    ## extract final message from chat data
    def getmessage(x):
        res = re.search(": .*",x)
        if res != None:
            return res.group()[2:]
        else:
            return None

    df["Message"] = list(map(getmessage,df.iloc[:,0]))


    ## Drop column 0
    df = df.drop(0,axis =1)

    total_user = len(df["sender"].unique())
    # print("Total Unique User = ",total_user)

    ## Preparing data for visualisation

    ## Find unique members in group
    group_members = list(set(df["sender"]))

    # print("Group Member = ", group_members)


    ## Find count of messages shared by each member
    n_message = list(map(lambda x : len(np.where(df["sender"]==x)[0]),group_members)) 

    ## Create a dataframe to store above values
    activity_data = pd.DataFrame({"sender": group_members,"n_count":n_message})
    ## Sort data for convenience and rearrange index
    activity_data = activity_data.sort_values(by=["n_count"], ascending=False)
    activity_data.index = range(0,len(activity_data))

    ## creating groups of data by time meridian
    timemeridian = df.groupby(by = "AmPm")

    amhours = timemeridian.get_group("am")
    pmhours = timemeridian.get_group("pm")

    ## getting hourly activity counts
    amhourcounts = amhours.Hour.value_counts().sort_index()
    pmhourcounts = pmhours.Hour.value_counts().sort_index()

    ## Most active members in group
    f = len(group_members)
    if f > 50:
        f = 50
    X = activity_data["sender"][:f]
    Y = activity_data.n_count[:f]

    plt.figure(figsize=[24,10])

    plt.title("Top {} Active Members".format(f), size = 16)

    plt.bar(x = X, height= Y, color = colorlist[1])
    plt.xticks(rotation = 80, size = 12)
    plt.yticks(size = 12)

    for i in range(0,f):
        plt.annotate(text = Y[i], xy = (i-0.25,Y[i]+5), size = 12)
    plt.savefig(path +'top_active_member.png', bbox_inches='tight')
    # plt.show()

    fig = plt.figure(figsize=[20,10])


    fig.suptitle("Activity wrt Time ", size = 16)

    gs = GridSpec(2,3) # 2 rows and 3 columns
    ax1 = fig.add_subplot(gs[0,0]) # first row, first col
    ax2 = fig.add_subplot(gs[0,1]) # first row, second col
    ax3 = fig.add_subplot(gs[1,0]) # second row, first col
    ax4 = fig.add_subplot(gs[1,1]) # second row, second col
    ax5 = fig.add_subplot(gs[:,2]) # all row, third col

    # Pie plot for messages shared in AM time meridian
    ax1.pie(amhourcounts.values, labels = amhourcounts.index,colors=colorlist , pctdistance=1, shadow=True, labeldistance=1.2)
    ax1.set_title("AM")
    # Bar plot for messages shared in AM time meridian
    ax2.bar(amhourcounts.index,amhourcounts.values,color=colorlist[3])

    # Pie plot for messages shared in PM time meridian
    ax3.pie(pmhourcounts.values, labels = pmhourcounts.index,colors=colorlist, pctdistance=1, shadow=True, labeldistance=1.2)
    ax3.set_title("PM")
    # Bar plot for messages shared in PM time meridian
    ax4.bar(pmhourcounts.index,pmhourcounts.values,color=colorlist[3])

    # Bar plot showing AM vs PM
    ax5.bar(["AM","PM"], [len(amhours),len(pmhours)],color=colorlist[13])
    ax5.annotate(text = str(round(100*len(amhours)/(len(amhours)+len(pmhours)))) + "%", xy = [0,len(amhours)/2], color = "white", size = 14, horizontalalignment = "center")
    ax5.annotate(text = str(round(100*len(pmhours)/(len(amhours)+len(pmhours)))) + "%", xy = [1,len(pmhours)/2], color = "white", size = 14, horizontalalignment = "center")

    plt.savefig(path+'activity_wrt_time.png', bbox_inches='tight')
    # plt.show()

    #top 10 active days
    top_10_active_days = df['Date'].value_counts().rename_axis('unique_values').to_frame('counts')

    top_10_active_days.sort_values('counts',inplace=True)
    avg_msg_per_day = top_10_active_days.mean()
    # print('Avg msg per day ',round(avg_msg_per_day[0],0))
    avg_msg_per_day_num = round(avg_msg_per_day[0],0)
    top_10_active_daysnew = top_10_active_days[-10:]

    # top_10_active_daysnew

    fig, ax = plt.subplots(figsize=(7,4))
    top_10_active_daysnew.plot(kind='barh', legend = False, ax=ax, color = colorlist[12])
    ax.set_title('top 10 busy days')
    ax.set_xlabel('chat count')
    ax.set_ylabel('date')
    fig.savefig(path+'top_busy_days.png', bbox_inches='tight')

    format = '%d/%m/%y %H:%M'
    df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format=format)
    df_date = df.set_index(pd.DatetimeIndex(df['Datetime']))
    plt.figure(figsize=[15,7])
    df_date.groupby('Date').count()['Day'].plot(style=['-'],color=colorlist[15])
    plt.ylabel('total message count');
    plt.title("MSG count wrt time")
    plt.savefig(path+'timeseries_masg_count.png', bbox_inches='tight')

    total_media = df['Message'].astype(str).apply(lambda x: 1 if ('media omitted') in x.lower() else 0).value_counts()
    # print("total media file shared = ", total_media[1])
    total_media_file_shared = total_media[1]


    df['Media'] = df['Message'].astype(str).apply(lambda x: 1 if ('media omitted') in x.lower() else 0)
    # media = df[df['Media'] == 1].groupby('sender').count()['Day']
    media = df[df['Media'] == 1]['sender'].value_counts().rename_axis('Members').to_frame('counts')
    # print("Members sharing most media = ",media.iloc[:10])
    f2= len(group_members)
    if f2 > 11:
        f = 10
    X = media.index[:f2]
    Y = media.counts[:f2]

    plt.figure(figsize=(15,7))
    chart = sns.barplot(x = X,y =Y)
    plt.xticks(rotation = 90)
    plt.title("Top {} members who share media".format(f2), loc='center')
    plt.savefig(path+'top_media_member.png', bbox_inches='tight')


    words = " ".join(df['Message'])

    def punctuation_stop(text):
        """remove punctuation and stop words"""
        filtered = []
        stop_words = set(STOPWORDS)
        word_tokens = text.split()
        for w in word_tokens:
            if w not in stop_words and w.isalpha():
                filtered.append(w.lower())
        return filtered


    words_filtered = punctuation_stop(words)

    text = " ".join([ele for ele in words_filtered])

    wc= WordCloud(background_color="white", random_state=1,stopwords=STOPWORDS, max_words = 50, width =1000, height = 1500)
    wc.generate(text)

    plt.figure(figsize=[15,15])
    plt.imshow(wc,interpolation="bilinear")
    plt.axis('off')
    plt.savefig(path+'word_cloud.png', bbox_inches='tight')


    def split_count(text):

        emoji_list = []
        data = regex.findall(r'\X', text)
        for word in data:
            if any(char in emoji.UNICODE_EMOJI for char in word):
                emoji_list.append(word)

        return emoji_list

    df["emoji"] = df["Message"].apply(split_count)

    emojis = sum(df['emoji'].str.len())
    # print("total emojies used = ",emojis)

    df2 = df[df['Message'] == '<Media omitted>']
    df = df.drop(df2.index)
    df['Letter_Count'] = df['Message'].apply(lambda s : len(s))
    df['Word_Count'] = df['Message'].apply(lambda s : len(s.split(' ')))
    df["MessageCount"]=1
    # print("average letter per message = ",round(df['Letter_Count'].mean(),0))
    # print("average word per message = ",round(df['Word_Count'].mean(),0))
    # print("total letters = ",df['Letter_Count'].sum())
    # print("total word = ",df['Word_Count'].sum())
    average_letter_per_message = round(df['Letter_Count'].mean(),0)
    average_word_per_message = round(df['Word_Count'].mean(),0)
    total_letters = df['Letter_Count'].sum()
    total_word = df['Word_Count'].sum()

    emoji_ctr = Counter()
    emojis_list = map(lambda x: ''.join(x.split()), emoji.UNICODE_EMOJI.keys())
    r = re.compile('|'.join(re.escape(p) for p in emojis_list))
    for idx, row in df.iterrows():
        emojis_found = r.findall(row["Message"])
        for emoji_found in emojis_found:
            emoji_ctr[emoji_found] += 1


    top10emojis = pd.DataFrame()
    # top10emojis = pd.DataFrame(data, columns={"emoji", "emoji_description", "emoji_count"}) 
    top10emojis['emoji'] = [''] * 10
    top10emojis['emoji_count'] = [0] * 10
    top10emojis['emoji_description'] = [''] * 10

    i = 0
    for item in emoji_ctr.most_common(10):
        # will be using another helper column, since during visualization, the emojis won't be rendered.
        description = emoji.demojize(item[0])[1:-1]    # using `[1:-1]` to remove the colons ':' at the end of the demojized strin
        
        # appending top 10 data of emojis.  # Loading into a DataFrame.
        top10emojis.emoji[i] = item[0]
        top10emojis.emoji_count[i] = int(item[1])
        top10emojis.emoji_description[i] = description
        i += 1

    # top10emojis.emoji = top10emojis.emoji.str.encode('unicode-escape')
    # print(top10emojis)
    # top10emojis['emoji']  = top10emojis['emoji'].astype(object).apply(lambda x: 'U+{:X}'.format(chr(x)))
    # print('=' * 60)
    # print(top10emojis)
    # print('=' * 60)

    ini_time = df_date.index[0]
    fin_time = df_date.index[-1]
    tot_time = fin_time - ini_time


    # print("chat started datetime -{} {}".format(ini_time,df['AmPm'].iat[0]))
    # print("last chat datetime -{} {}".format(ini_time,df['AmPm'].iat[-1]))
    # print("out of {} days {} days members pinged".format(tot_time.days,df['Date'].nunique()) )

    chat_started_datetime = "Chat started on -{} {}".format(ini_time,df['AmPm'].iat[0])
    last_chat_datetime ="Last chat on -{} {}".format(ini_time,df['AmPm'].iat[-1])
    sttoend  = "Out of {} days {} days members pinged.".format(tot_time.days,df['Date'].nunique())


    total_deleted_messages = df[df['Message'].str.contains("message was deleted")]['Day'].count()
    # print("total messages deleted {}".format(total_deleted_messages))

    cmnwrd = Counter(text.split()).most_common(50)

    wrd= []
    cnt=[]
    for i in cmnwrd:
        wrd.append(i[0])
        cnt.append(i[1])

    plt.figure(figsize=(10,7))

    chart = sns.barplot(x = wrd,y =cnt, palette="cubehelix")
    plt.xticks(rotation = 90)
    plt.title("Top used words", loc='center')
    plt.savefig(path+'top_used_words.png', bbox_inches='tight')


    df['sentiment'] = df['Message'].astype(str).apply(lambda x: TextBlob(x.lower()).sentiment.polarity)
    df["sent"] = df['sentiment'].astype(float).apply(lambda x: "P" if x>0 else ("O" if x==0 else "N"))

    total_sent = df['sent'].count()
    neu_sent = df['sent'].value_counts()[0]
    neg_sent = df['sent'].value_counts()[1]
    pos_sent = df['sent'].value_counts()[2]

    # print("out of {} messages {} have positive sentiment, {} have negative sentiment and {} neutral sentiment".format(total_sent,pos_sent, neg_sent,neu_sent) )
    sentmnt = """Out of {} messages 
            {} have positive sentiment, 
            {} have negative sentiment and 
            {} neutral sentiment.""".format(total_sent,pos_sent, neg_sent,neu_sent)


    labels = ['positive', 'negative', 'neutral']
    sizes = [pos_sent,neg_sent,neu_sent]

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, colors=[colorlist[6],colorlist[4],colorlist[12]])
    ax1.axis('equal')
    plt.title('sentiment analysis')
    plt.savefig(path+'sentiment.png', bbox_inches='tight')

    return [total_user,group_members, avg_msg_per_day_num,total_media_file_shared,emojis,average_letter_per_message,average_word_per_message ,total_letters,total_word,top10emojis,chat_started_datetime,last_chat_datetime,sttoend,total_deleted_messages,sentmnt]
