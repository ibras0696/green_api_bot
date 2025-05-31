from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Integer, String, Column, Text, ForeignKey, Date, Boolean
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UUID
from sqlalchemy.orm import relationship

Base = declarative_base()





class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=True)  # Может быть только Telegram
    whatsapp_id = Column(String(100), unique=True, nullable=True)  # Или только WhatsApp
    day_count = Column(Integer, default=3)  # Кол-во дней подписки
    is_active = Column(Boolean, default=True)  # Активна или нет
    created_at = Column(DateTime, default=datetime.utcnow)  # Дата создания

    # # Связь с подписками
    # subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete")

    def __repr__(self):
        return f"<User id={self.id} telegram_id={self.telegram_id} whatsapp_id={self.whatsapp_id}>"

#
# class Subscription(Base):
#     __tablename__ = "subscriptions"
#
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     day_count = Column(Integer, default=3)  # Кол-во дней подписки
#     is_active = Column(Boolean, default=True)  # Активна или нет
#     created_at = Column(DateTime, default=datetime.utcnow)  # Дата создания
#
#     # Связь с пользователем
#     user = relationship("User", back_populates="subscriptions")
#
#     def __repr__(self):
#         return f"<Subscription id={self.id} user_id={self.user_id} days={self.day_count} active={self.is_active}>"


# class Users(Base):
#     __tablename__ = 'users'
#     id = Column(Integer, primary_key=True)
#
#     telegram_id = Column(Integer, nullable=True, unique=True)
#     whatsapp_id = Column(String(100), nullable=True, unique=True)
#     day_count = Column(Integer, nullable=True)

# class User(Base):
#     """
#     Таблица пользователей.
#     Хранит Telegram ID и имя (если нужно).
#     """
#     __tablename__ = "users"
#
#     id = Column(Integer, primary_key=True)
#     telegram_id = Column(Integer, unique=True, index=True)  # Уникальный Telegram ID пользователя
#     name = Column(String, nullable=True)  # Необязательное имя
#
#     # Связь: один пользователь может иметь много подписок
#     subscriptions = relationship("UserSubscription", back_populates="user")
#
#
# class Subscription(Base):
#     """
#     Таблица подписок.
#     Описывает тип подписки: название и сколько она длится.
#     """
#     __tablename__ = "subscriptions"
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String, unique=True)  # Уникальное имя подписки (например "Стандарт")
#     duration_days = Column(Integer, default=30)  # Сколько дней длится подписка
#
#     # Связь: одна подписка может быть выдана многим пользователям
#     user_subscriptions = relationship("UserSubscription", back_populates="subscription")
#
#
# class UserSubscription(Base):
#     """
#     Таблица привязки пользователя к подписке.
#     Хранит дату начала, дату окончания и оставшиеся использования.
#     """
#     __tablename__ = "user_subscriptions"
#
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id"))  # ID пользователя
#     subscription_id = Column(Integer, ForeignKey("subscriptions.id"))  # ID подписки
#     start_date = Column(DateTime, default=datetime.datetime.utcnow)  # Когда началась подписка
#     end_date = Column(DateTime)  # Когда закончится
#     remaining_uses = Column(Integer, default=30)  # Сколько осталось использований
#
#     # Обратные связи
#     user = relationship("User", back_populates="subscriptions")
#     subscription = relationship("Subscription", back_populates="user_subscriptions")