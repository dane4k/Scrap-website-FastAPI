from sqlalchemy import create_engine, func, Column, Integer, String, DateTime, Table, MetaData
from sqlalchemy.orm import sessionmaker
import matplotlib.pyplot as plt


def print_table(table_name, n):
    for row in session.query(table_name).limit(n).all():
        print(row)


def plot_hists(query):
    results = query.all()

    months_2023 = []
    months_2022 = []
    for result in results:
        month, count = result
        if month[:4] == '2023':
            months_2023.append(month[5:])
        elif month[:4] == '2022':
            months_2022.append(month[5:])

    counts_2023 = []
    counts_2022 = []
    for result in results:
        month, count = result
        if month[:4] == '2023':
            counts_2023.append(count)
        elif month[:4] == '2022':
            counts_2022.append(count)

    plt.bar(months_2022, counts_2022)
    plt.xlabel('Месяц')
    plt.ylabel('Количество сообщений')
    plt.title('Количество сообщений в 2022 году')
    plt.show()

    plt.bar(months_2023, counts_2023)
    plt.xlabel('Месяц')
    plt.ylabel('Количество сообщений')
    plt.title('Количество сообщений в 2023 году')
    plt.show()


if __name__ == '__main__':
    metadata = MetaData()

    engine = create_engine('sqlite:///database.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    comment_table = Table('Comment', metadata, Column('id_', Integer, primary_key=True), Column('theme_id', Integer),
                          Column('author_id', Integer), Column('author_name', String), Column('quote_id', Integer),
                          Column('text', String), Column('created', DateTime))

    theme_table = Table('Theme', metadata, Column('id_', Integer, primary_key=True),
                        Column('name', String), Column('text', String))

    author_table = Table('Author', metadata, Column('id_', Integer, primary_key=True), Column('nickname', String))

    plot_query = session.query(func.strftime('%Y-%m', comment_table.c.created).label('month'),
                               func.count('*').label('count')).filter(
        func.strftime('%Y', comment_table.c.created).in_(['2023', '2022'])).group_by('month').order_by('month')

    n_rows = 10

    print(f"\n\nПервые {n_rows} строк таблицы Theme: \n\n")
    print_table(theme_table, n_rows)

    print(f"\n\nПервые {n_rows} строк таблицы Author: \n\n")
    print_table(author_table, n_rows)

    print(f"\n\nПервые {n_rows} строк таблицы Comment: \n\n")
    print_table(comment_table, n_rows)

    plot_hists(plot_query)

    session.close()
