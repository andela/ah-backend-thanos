def read_time(article_body):
    WPM = 267
    WORD_LENGTH = 3
    total_words = 0
    for article_text in article_body:
        total_words += len(article_text.split())/WORD_LENGTH
    return round(total_words/WPM)
