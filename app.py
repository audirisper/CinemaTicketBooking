import random
import sqlite3
import fpdf
import string
from fpdf import FPDF


class User:
    """Represents a user That buys a cinema seat """

    def __init__(self, name):
        self.name = name

    def buy(self, seat, card):
        """Buys a ticket if the card is valid"""
        if seat.is_free():
            if card.validate(price=seat.get_price()):
                seat.occupy()
                ticket = Ticket(user=self, price=seat.get_price(), seat_number=0)
                ticket.to_pdf()
                return "Purchase Was Successful"
            else:
                return "There was a problem with your card"
        else:
            return " The seat is taken"


class Seat:
    """Represents a cinema seat that can be taken by a user"""
    database = "cinema.db"

    def __init__(self, seat_id):
        self.seat_id = seat_id

    def get_price(self):
        """Get the price of a certain seat"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        query = "SELECT price FROM seat WHERE seat_id = ?"
        cursor.execute(query, [self.seat_id])
        price = cursor.fetchall()[0][0]
        conn.close()
        return price

    def is_free(self):
        """Check in the database if seat is taken or not"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        query = "SELECT taken FROM seat WHERE seat_id = ?"
        cursor.execute(query, [self.seat_id])
        result = cursor.fetchall()[0][0]
        conn.close()

        if result == 0:
            return True
        else:
            return False

    def occupy(self):
        """Change value of taken in the database from 0 to 1nif seat is free"""
        if self.is_free():
            conn = sqlite3.connect(self.database)
            cursor = conn.cursor()
            query = "UPDATE seat SET taken = ? WHERE seat_id = ?"
            cursor.execute(query, [1, self.seat_id])
            conn.commit()
            conn.close()


class Card:
    """Represents a bank card needed to finalize a seat purchase """
    database = "cinema.db"

    def __init__(self, type, number, cvc, holder):
        self.type = type
        self.number = number
        self.cvc = cvc
        self.holder = holder

    def validate(self, price):
        """Checks if card is valid and has balance, subtracts price from balance"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        query = "SELECT balance FROM card WHERE number = ? AND cvc = ?"
        cursor.execute(query, [self.number, self.cvc])
        result = cursor.fetchall()

        if result:
            balance = result[0][0]
            query = "UPDATE card SET balance = ? WHERE number = ? AND cvc = ?"
            cursor.execute(query, [balance - price, self.number, self.cvc])
            conn.commit()
            conn.close()
            return True


class Ticket:
    """Represents a cinema ticket purchased by a user"""

    def __init__(self, user, price, seat_number):
        self.seat_number = seat_number
        self.user = user
        self.price = price
        self.id = "".join([random.choice(string.ascii_uppercase) for i in range(8)])

    def to_pdf(self):
        """Creates a pdf ticket"""
        pdf = FPDF(orientation="P", unit="pt", format="A4")
        pdf.add_page()
        # The header of the pdf
        pdf.set_font(family='Times', style='B', size=24)
        pdf.cell(w=0, h=80, txt="CPL Digital Ticket", border=1, ln=1, align="C")
        # Ticket Name
        pdf.set_font(family="Times", style="B", size=14)
        pdf.cell(w=100, h=25, txt="Name: ", border=1)
        pdf.set_font(family="Times", style="B", size=12)
        pdf.cell(w=0, h=25, txt=self.user.name, border=1, ln=1)
        # The ticket id
        pdf.set_font(family="Times", style="B", size=14)
        pdf.cell(w=100, h=25, txt="Ticket_id: ", border=1)
        pdf.set_font(family="Times", style="B", size=12)
        pdf.cell(w=0, h=25, txt=self.id, border=1, ln=1)
        # The seat number
        pdf.set_font(family="Times", style="B", size=14)
        pdf.cell(w=100, h=25, txt="Seat_number: ", border=1)
        pdf.set_font(family="Times", style="B", size=12)
        pdf.cell(w=0, h=25, txt=self.seat_number, border=1, ln=1)
        # The price
        pdf.set_font(family="Times", style="B", size=14)
        pdf.cell(w=100, h=25, txt="Seat_Price: ", border=1)
        pdf.set_font(family="Times", style="B", size=12)
        pdf.cell(w=0, h=25, txt=f"{self.price}", border=1, ln=1)

        # Generate the pdf
        pdf.output("cinema.pdf", "F")


# Test the app
if __name__ == '__main__':
    name = input("Your full Name: ")
    seat_id = input("Preferred seat number: ")
    card_type = input("Your card type: ")
    card_number = input("Your card number: ")
    card_cvc = input("Your card cvc: ")
    card_holder = input("Crd holder name: ")

    # Create our objects
    user = User(name)
    seat = Seat(seat_id)
    card = Card(card_type, card_number, card_cvc, card_holder)

    print(user.buy(seat, card))
