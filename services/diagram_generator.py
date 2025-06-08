from services.database import User
import matplotlib.pyplot as plt
from io import BytesIO
from services.database import get_session, Expense


def generate_pie_chart(telegram_id: int) -> BytesIO:
    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            return None

        expenses = session.query(Expense).filter_by(user_id=user.id).all()

        categories = {}
        for expense in expenses:
            if expense.category not in categories:
                categories[expense.category] = 0
            categories[expense.category] += expense.amount

        if not categories:
            return None

        labels = list(categories.keys())
        sizes = list(categories.values())

        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')
        plt.title('Статистика расходов')

        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        plt.close()

        return img_buffer
    finally:
        session.close()