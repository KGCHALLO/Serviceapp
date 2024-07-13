from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
import datetime
import json
import os

class Customer(BoxLayout):
    customer_name = ObjectProperty(None)
    service_date = ObjectProperty(None)

class MyWidget(BoxLayout):
    customer_list = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MyWidget, self).__init__(**kwargs)
        self.load_customers()

    def add_customer(self):
        name = self.ids.customer_name.text
        service_date = self.ids.service_date.text

        if name and service_date:
            customer = {"name": name, "service_date": service_date}
            self.ids.customer_list.add_widget(Label(text=f"{name} - {service_date}"))
            self.save_customer(customer)

    def save_customer(self, customer):
        filename = "customers.json"
        if os.path.exists(filename):
            with open(filename, "r") as file:
                customers = json.load(file)
        else:
            customers = []

        customers.append(customer)

        with open(filename, "w") as file:
            json.dump(customers, file)

    def load_customers(self):
        filename = "customers.json"
        if os.path.exists(filename):
            with open(filename, "r") as file:
                customers = json.load(file)

            for customer in customers:
                self.ids.customer_list.add_widget(Label(text=f"{customer['name']} - {customer['service_date']}"))

class MyApp(App):
    def build(self):
        return MyWidget()

if __name__ == '__main__':
    MyApp().run()
