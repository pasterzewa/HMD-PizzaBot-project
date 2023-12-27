# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict



class ActionChangeOrder(Action):
	def name(self):
		return 'action_change_order'

	def run(self, dispatcher, tracker, domain):
		pizza_size = tracker.get_slot("pizza_size")
		pizza_type = tracker.get_slot("pizza_type")
		pizza_amount = tracker.get_slot("pizza_amount")
		SlotSet("pizza_type", pizza_type)
		SlotSet("pizza_size", pizza_size)
		SlotSet("pizza_amount", pizza_amount)
		return[]

class ActionPizzaOrderAdd(Action):
	def name(self):
		return 'action_pizza_order_add'

	def run(self, dispatcher, tracker, domain):
		pizza_size = tracker.get_slot("pizza_size")
		pizza_type = tracker.get_slot("pizza_type")
		pizza_amount = tracker.get_slot("pizza_amount")
		if pizza_size is None:
			pizza_size = "standard"
		order_details =  str(pizza_amount + " "+pizza_type + " is of "+pizza_size )
		old_order = tracker.get_slot("total_order")
		return[SlotSet("total_order", [order_details]) if old_order is None else SlotSet("total_order", [old_order[0]+' and '+order_details])]

class ActionResetPizzaForm(Action):
	def name(self):
		return 'action_reset_pizza_form'

	def run(self, dispatcher, tracker, domain):

		return[SlotSet("pizza_type", None),SlotSet("pizza_size", None),SlotSet("pizza_amount", None)]

class ActionOrderNumber(Action):
	def name(self):
		return 'action_order_number'

	def run(self, dispatcher, tracker, domain):
		name_person = tracker.get_slot("client_name")
		number_person = tracker.get_slot("phone_number")
		order_number =  str(name_person + "_"+number_person)
		print(order_number)
		return[SlotSet("order_number", order_number)]


class ActionGetRestaurantLocation(Action):
	def name(self):
		return 'action_get_restaurant_location'

	def run(self, dispatcher, tracker, domain):

		restaurant_address = "Via Giuseppe Verdi, 15, 38122 Trento TN"

		return[SlotSet("restaurant_location", restaurant_address)]


# for a generic slot validation please refer to https://rasa.com/docs/action-server/validation-action/
class ValidatePizzaOrderForm(FormValidationAction):

	def name(self) -> Text:
		# https://rasa.com/docs/rasa/forms/#advanced-usage
		return "validate_pizza_order_form"

	@staticmethod
	def pizza_db() -> List[Text]:
		"""Database of supported cuisines"""

		return ["hawaii", "funghi", "french"]

	def validate_pizza_type(
		self,
		slot_value: Any,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: DomainDict,
	) -> Dict[Text, Any]:
		"""Validate cuisine value."""

		if isinstance(slot_value, str):
			if slot_value.lower() in self.pizza_db():
				# validation succeeded, set the value of the "cuisine" slot to value
				return {"pizza_type": slot_value}
			else:
				return {"pizza_type": "Special " + slot_value.title() }
		elif isinstance(slot_value, list):
			if len(slot_value) > 0:
				concatenated_slot = ", ".join(slot_value)
				return {"pizza_type": concatenated_slot}
			else:
				# validation failed, set this slot to None so that the
				# user will be asked for the slot again
				return {"pizza_type": None}