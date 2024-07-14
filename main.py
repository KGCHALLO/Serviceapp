import datetime
import csv

import task
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

from kivy.core.text import LabelBase


# Add custom font (adjust the path to your font file)
LabelBase.register(name='Roboto',
                   fn_regular='Roboto-Regular.ttf',
                   fn_bold='Roboto-Bold.ttf')


def read_customers(file_name):
    customers = []
    try:
        with open(file_name, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                row['last_service_date'] = datetime.datetime.strptime(row['last_service_date'], '%Y-%m-%d').date()
                customers.append(row)
    except FileNotFoundError:
        pass
    return customers


def write_customers(file_name, customers):
    with open(file_name, mode='w', newline='') as file:
        fieldnames = ['first_name', 'last_name', 'num_air_conditioners', 'last_service_date']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for customer in customers:
            writer.writerow(customer)


class ACServiceReminderApp(App):

    def build(self):
        self.data_file_name = 'customers.csv'
        self.customers = read_customers(self.data_file_name)
        self.service_interval_days = 150

        self.layout = FloatLayout()

        # Add background image with adjusted opacity
        background = Image(source='background.jpg', allow_stretch=True, keep_ratio=False,
                           size_hint=(None, None), size=(Window.width, Window.height))
        background.opacity = 0.4  # Adjust opacity as needed
        self.layout.add_widget(background)

        self.content_layout = BoxLayout(orientation='vertical', padding=10, spacing=10,
                                        size_hint=(0.9, 0.9), pos_hint={'center_x': 0.5, 'center_y': 0.5})

        self.scrollview = ScrollView(size_hint=(1, 1))
        self.customer_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.scrollview.add_widget(self.customer_list)

        # Set background color directly on the customer_list BoxLayout
        self.customer_list.background_color = (1, 1, 1, 0.7)  # Adjust color and opacity as needed

        self.refresh_customer_list()
        self.content_layout.add_widget(self.scrollview)
        self.add_buttons()

        self.layout.add_widget(self.content_layout)
        return self.layout

    # Other methods and button bindings remain unchanged...

    def check_service_reminder(self):
        today = datetime.date.today()
        reminders = []
        for customer in self.customers:
            last_service_date = customer['last_service_date']
            service_due_date = last_service_date + datetime.timedelta(days=self.service_interval_days)
            if today >= service_due_date:
                reminders.append(customer)
        return reminders

    def display_reminders(self, instance):
        self.reminders = self.check_service_reminder()
        reminder_text = ""
        for reminder in self.reminders:
            reminder_text += f"Reminder: {reminder['first_name']} {reminder['last_name']} needs their air conditioners serviced.\n"
        popup = Popup(title='Service Reminders', content=Label(text=reminder_text if reminder_text else "No reminders due."),
                      size_hint=(None, None), size=(400, 400))
        popup.open()

    def add_customer(self, instance):
        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_content.add_widget(Label(text='First Name'))
        self.first_name_input = TextInput()
        popup_content.add_widget(self.first_name_input)

        popup_content.add_widget(Label(text='Last Name'))
        self.last_name_input = TextInput()
        popup_content.add_widget(self.last_name_input)

        popup_content.add_widget(Label(text='Number of Air Conditioners'))
        self.num_ac_input = TextInput()
        popup_content.add_widget(self.num_ac_input)

        popup_content.add_widget(Label(text='Last Service Date (YYYY-MM-DD)'))
        self.last_service_date_input = TextInput()
        popup_content.add_widget(self.last_service_date_input)

        popup_content.add_widget(Button(text='Add', on_release=self.add_customer_to_list))
        popup = Popup(title='Add Customer', content=popup_content, size_hint=(None, None), size=(400, 400))
        popup.open()

    def add_customer_to_list(self, instance):
        first_name = self.first_name_input.text
        last_name = self.last_name_input.text
        num_air_conditioners = self.num_ac_input.text
        last_service_date = self.last_service_date_input.text

        if not first_name or not last_name or not num_air_conditioners or not last_service_date:
            popup = Popup(title='Input Error', content=Label(text='All fields are required.'), size_hint=(None, None), size=(300, 200))
            popup.open()
            return

        try:
            num_air_conditioners = int(num_air_conditioners)
        except ValueError:
            popup = Popup(title='Input Error', content=Label(text='Number of air conditioners must be an integer.'), size_hint=(None, None), size=(300, 200))
            popup.open()
            return

        try:
            last_service_date = datetime.datetime.strptime(last_service_date, '%Y-%m-%d').date()
        except ValueError:
            popup = Popup(title='Input Error', content=Label(text='Date must be in YYYY-MM-DD format.'), size_hint=(None, None), size=(300, 200))
            popup.open()
            return

        new_customer = {
            "first_name": first_name,
            "last_name": last_name,
            "num_air_conditioners": num_air_conditioners,
            "last_service_date": last_service_date
        }

        self.customers.append(new_customer)
        write_customers(self.data_file_name, self.customers)
        self.refresh_customer_list()

        popup = Popup(title='Success', content=Label(text='Customer added successfully!'), size_hint=(None, None), size=(300, 200))
        popup.open()

    def refresh_customer_list(self):
        self.customer_list.clear_widgets()
        for customer in self.customers:
            customer_info = f"{customer['first_name']} {customer['last_name']} - Air Conditioners: {customer['num_air_conditioners']}"
            customer_label = Label(text=customer_info, font_name='Roboto', font_size=18, color=(0, 0, 0, 1))
            self.customer_list.add_widget(customer_label)

    def update_service_status(self, instance):
        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_content.add_widget(Label(text='Select Customer to Update'))
        customers_names = [f"{customer['first_name']} {customer['last_name']}" for customer in self.customers]
        self.customer_selection = TextInput(multiline=False)
        popup_content.add_widget(self.customer_selection)

        for name in customers_names:
            popup_content.add_widget(Button(text=name, on_release=self.update_selected_customer))

        popup_content.add_widget(Button(text='Update', on_release=self.update_service_status_final))
        popup = Popup(title='Update Service Status', content=popup_content, size_hint=(None, None), size=(400, 400))
        popup.open()

    def update_selected_customer(self, instance):
        self.selected_customer_name = instance.text

    def update_service_status_final(self, instance):
        selected_customer = None
        for customer in self.customers:
            if f"{customer['first_name']} {customer['last_name']}" == self.selected_customer_name:
                selected_customer = customer
                break

        if selected_customer:
            selected_customer['last_service_date'] = datetime.date.today()
            write_customers(self.data_file_name, self.customers)
            self.refresh_customer_list()
            popup = Popup(title='Success', content=Label(text=f"Service status updated for {selected_customer['first_name']} {selected_customer['last_name']}."), size_hint=(None, None), size=(400, 400))
            popup.open()
        else:
            popup = Popup(title='Error', content=Label(text='Customer not found.'), size_hint=(None, None), size=(300, 200))
            popup.open()

    def remove_customer(self, instance):
        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_content.add_widget(Label(text='Select Customer to Remove'))
        customers_names = [f"{customer['first_name']} {customer['last_name']}" for customer in self.customers]
        self.customer_selection_remove = TextInput(multiline=False)
        popup_content.add_widget(self.customer_selection_remove)

        for name in customers_names:
            popup_content.add_widget(Button(text=name, on_release=self.remove_selected_customer))

        popup_content.add_widget(Button(text='Remove', on_release=self.remove_customer_final))
        popup = Popup(title='Remove Customer', content=popup_content, size_hint=(None, None), size=(400, 400))
        popup.open()

    def remove_selected_customer(self, instance):
        self.selected_customer_name = instance.text

    def remove_customer_final(self, instance):
        selected_customer = None
        for customer in self.customers:
            if f"{customer['first_name']} {customer['last_name']}" == self.selected_customer_name:
                selected_customer = customer
                break

        if selected_customer:
            self.customers.remove(selected_customer)
            write_customers(self.data_file_name, self.customers)
            self.refresh_customer_list()
            popup = Popup(title='Success', content=Label(text=f"Customer {selected_customer['first_name']} {selected_customer['last_name']} removed successfully."), size_hint=(None, None), size=(400, 400))
            popup.open()
        else:
            popup = Popup(title='Error', content=Label(text='Customer not found.'), size_hint=(None, None), size=(300, 200))
            popup.open()

    def change_service_interval(self, instance):
        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_content.add_widget(Label(text='Enter new service interval in days'))
        self.new_interval_input = TextInput(multiline=False)
        popup_content.add_widget(self.new_interval_input)
        popup_content.add_widget(Button(text='Change', on_release=self.change_service_interval_final))
        popup = Popup(title='Change Service Interval', content=popup_content, size_hint=(None, None), size=(400, 400))
        popup.open()

    def change_service_interval_final(self, instance):
        try:
            new_interval = int(self.new_interval_input.text)
            if new_interval > 0:
                self.service_interval_days = new_interval
                popup = Popup(title='Success', content=Label(text=f"Service interval changed to {self.service_interval_days} days."), size_hint=(None, None), size=(400, 400))
                popup.open()
            else:
                popup = Popup(title='Error', content=Label(text='Interval must be a positive integer.'), size_hint=(None, None), size=(300, 200))
                popup.open()
        except ValueError:
            popup = Popup(title='Error', content=Label(text='Interval must be a valid number.'), size_hint=(None, None), size=(300, 200))
            popup.open()

    def add_buttons(self):
        button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, None), height=50)

        add_customer_button = Button(text='Add Customer', size_hint=(None, None), width=150, height=50)
        add_customer_button.bind(on_release=self.add_customer)

        update_service_status_button = Button(text='Update Service Status', size_hint=(None, None), width=200, height=50)
        update_service_status_button.bind(on_release=self.update_service_status)

        remove_customer_button = Button(text='Remove Customer', size_hint=(None, None), width=150, height=50)
        remove_customer_button.bind(on_release=self.remove_customer)

        change_service_interval_button = Button(text='Change Service Interval', size_hint=(None, None), width=200, height=50)
        change_service_interval_button.bind(on_release=self.change_service_interval)

        check_reminders_button = Button(text='Check Service Reminders', size_hint=(None, None), width=250, height=50)
        check_reminders_button.bind(on_release=self.display_reminders)

        button_layout.add_widget(add_customer_button)
        button_layout.add_widget(update_service_status_button)
        button_layout.add_widget(remove_customer_button)
        button_layout.add_widget(change_service_interval_button)
        button_layout.add_widget(check_reminders_button)

        self.content_layout.add_widget(button_layout)


if __name__ == '__main__':
    ACServiceReminderApp().run()


