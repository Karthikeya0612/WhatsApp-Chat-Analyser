from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
from better_profanity import profanity
import pandas as pd
import emoji

extractor = URLExtract()


def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]
    words = []
    links = []
    for message in df['messages']:
        words.extend(message.split())
        links.extend(extractor.find_urls(message))
    num_media = df[df['messages'] == '<Media omitted>\n'].shape[0]

    return num_messages, len(words), num_media, len(links)


def most_active_user(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x, df


def create_wordcloud(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    df_wc = wc.generate(df['messages'].str.cat(sep=" ").replace("<Media omitted>", ""))
    return df_wc


def most_common_words(selected_user, df):
    f = open('stop_words.txt', 'r')
    stop_words = f.read()
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    temp = df[df['user'] != 'group_notifications']
    temp = temp[temp['messages'] != '<Media omitted>\n']
    words_used = []
    for m in temp['messages']:
        for word in m.lower().split():
            if word not in stop_words:
                words_used.append(word)
    return pd.DataFrame(Counter(words_used).most_common(20))


def emoji_count(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    emojis = []
    for message in df['messages']:
        emojis.extend(c for c in message if c in emoji.UNICODE_EMOJI['en'])
    if len(emojis) == 0:
        return None
    return pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))


def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    timeline = df.groupby(['year', 'month_num', 'month']).count()['messages'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    timeline['time'] = time
    return timeline


def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df.groupby('modified_date').count()['messages'].reset_index()


def week_activity(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['day_name'].value_counts()


def month_activity(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df.pivot_table(index='day_name', columns='period', values='messages', aggfunc='count').fillna(0)


def profanity_check(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    profane_words = []
    for m in df['messages']:
        for word in m.lower().split():
            if word.isalpha():
                if profanity.contains_profanity(word):
                    profane_words.append(word)
    if len(profane_words) == 0:
        return None
    return pd.DataFrame(Counter(profane_words).most_common(20))
