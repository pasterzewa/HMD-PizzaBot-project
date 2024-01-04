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
from word2number import w2n
import re

class ActionChangeOrder(Action):
	def name(self):
		return 'action_change_order'

	def run(self, dispatcher, tracker, domain):
		pizza_size = tracker.get_slot("pizza_size")
		pizza_type = tracker.get_slot("pizza_type")
		pizza_amount = tracker.get_slot("pizza_amount")
		pizza_crust = tracker.get_slot("pizza_crust")
		pizza_sliced = tracker.get_slot("pizza_sliced")
		SlotSet("pizza_type", pizza_type)
		SlotSet("pizza_size", pizza_size)
		SlotSet("pizza_amount", pizza_amount)
		SlotSet("pizza_crust", pizza_crust)
		SlotSet("pizza_sliced", pizza_sliced)

		answer = "Your change has been noted."
		dispatcher.utter_message(text=answer)

		return[]

class ActionPizzaOrderAdd(Action):
	def name(self):
		return 'action_pizza_order_add'

	def run(self, dispatcher, tracker, domain):
		pizza_size = tracker.get_slot("pizza_size")
		pizza_type = tracker.get_slot("pizza_type")
		pizza_amount = tracker.get_slot("pizza_amount")
		pizza_crust = tracker.get_slot("pizza_crust")
		pizza_sliced = tracker.get_slot("pizza_sliced")
		if pizza_size is None:
			pizza_size = "standard"
		sliced = ""
		if pizza_sliced: # must test it!
			sliced = "sliced"
		else:
			sliced = "not sliced"
		order_details =  str(pizza_amount + " "+pizza_type + " of size "+pizza_size + " on " + pizza_crust + " crust, " + sliced)
		old_order = tracker.get_slot("total_order")

		cost = 0 if tracker.get_slot("order_cost") is None else int(tracker.get_slot("order_cost"))
		# pizza_amount - multiplies the cost for that pizza
		amount_multipier = w2n.word_to_num(pizza_amount)
		# pizza_size - multiplies 0.8, 1, 1.2, 1.5 based on size; using synonyms I should have this value with number of inches
		size_multiplier = 1
		if '10' in pizza_size:
			size_multiplier = 0.8
		elif '12' in pizza_size:
			size_multiplier = 1
		elif '14' in pizza_size:
			size_multiplier = 1.2
		elif '18' in pizza_size:
			size_multiplier = 1.5
		# pizza_crust - stuffed adds 2 euros, flat bread and cracker add 1, thin is the default so it doesn't add anything
		crust_bonus = 0
		if pizza_crust.lower() == 'stuffed':
			crust_bonus = 2
		elif pizza_crust.lower() == 'flat bread' or pizza_crust.lower() == 'cracker':
			crust_bonus = 1
		# pizza_type - Margherita is only 7 euros and that's the base for all pizzas
		# if it's some pizza with one word (Hawaiian, Pepperoni, etc.) then we treat it as a 'normal' pizza with ingredients and it's 10 euros
		# a special pizza adds 2 euros per ingredient
		type_cost = 7
		if "special" in pizza_type.lower():
			count_and = pizza_type.lower().count(' and ')
			count_comma = pizza_type.lower().count(',')
			count_space = pizza_type.lower().count(' ')
			count = count_and + count_comma
			if count == 0:
				count = count_space # special case when client was too lazy for punctuation and proper grammar
			type_cost += 2*count
		elif pizza_type.lower() != 'margherita':
			type_cost = 10

		cost += (type_cost + crust_bonus)*size_multiplier*amount_multipier

		return[SlotSet("total_order", [order_details]) if old_order is None else SlotSet("total_order", [old_order[0]+' and '+order_details]),
		 		SlotSet("order_cost", cost)]

class ActionResetPizzaForm(Action):
	def name(self):
		return 'action_reset_pizza_form'

	def run(self, dispatcher, tracker, domain):

		return[SlotSet("pizza_type", None),SlotSet("pizza_size", None),SlotSet("pizza_amount", None),SlotSet("pizza_crust", None),SlotSet("pizza_sliced", None)]

class ActionOrderNumber(Action):
	def name(self):
		return 'action_order_number'

	def run(self, dispatcher, tracker, domain):
		name_person = tracker.get_slot("client_name")
		number_person = tracker.get_slot("phone_number")
		order_number =  str(re.sub("\s", "_", name_person) + "_"+number_person)
		print(order_number)
		return[SlotSet("order_number", order_number)]

class ActionCheckPromotion(Action):
	def name(self):
		return 'action_check_promotion'

	def run(self, dispatcher, tracker, domain):
		promotion = tracker.get_slot("possible_promotion")
		ok = False
		if promotion == "2+1 Large Pizzas":
			# check if in the total order we have either three times the word "16" or
			# split the orders by word 'and', and in a loop calculate pizza amount (amount is the first word) of pizzas with "16"
			# again using w2n
			print("abba")
		elif promotion == "2 Margheritas For The Price of 1":
			# check if the order contains either "two/2 Margherita" or at least twice the word "Margherita"
			print("abba")
		elif promotion == "XL Pizza + Small Pepperoni Pizza For Half-Price":
			# split the order using ' and 'and check if at least one is 18" and one is a small pepperoni
			print("abba")
		else:
			print("wrong promotion")

		if ok:
			return[SlotSet("promotion", promotion)]
		else:
			return[]
	
class ActionSuggestPromotion(Action):
	def name(self):
		return 'action_suggest_promotion'

	def run(self, dispatcher, tracker, domain):
		order = tracker.get_slot("total_order")
		promotion = None
		ok = False

		# "2+1 Large Pizzas"
		# check if the user has at least two large pizzas
		# if 3 already - set the possible_promotion_conditions_met to True

		# "2 Margheritas For The Price of 1"
		# check if the user has at least one margherita
		# if 2 already - set the possible_promotion_conditions_met to True

		# "XL Pizza + Small Pepperoni Pizza For Half-Price":
		# check if the client has either pizza in size 18" or a small pepperoni
		# if both already - set the possible_promotion_conditions_met to True


		if ok:
			return[SlotSet("possible_promotion", promotion)]
		else:
			return[]

class ActionGetRestaurantLocation(Action):
	def name(self):
		return 'action_get_restaurant_location'

	def run(self, dispatcher, tracker, domain):

		restaurant_address = "Via Giuseppe Verdi, 15, 38122 Trento TN"

		return[SlotSet("restaurant_location", restaurant_address)]

class ActionGetMeatPizzas(Action):
	def name(self):
		return 'action_get_meat_pizzas'
	
	def run(self, dispatcher, tracker, domain):

		meat_pizzas = "Hawaii, Pepperoni, Ham, Bacon, Mortadella, Salami"
		answer = "Our restaurant has several meat options. They are "+ meat_pizzas + "."
		dispatcher.utter_message(text=answer)

		return []
		#return[SlotSet("meat_pizzas", meat_pizzas)]

class ActionGetVegePizzas(Action):
	def name(self):
		return 'action_get_vege_pizzas'
	
	def run(self, dispatcher, tracker, domain):

		vege_pizzas = "Funghi, Margherita, Artichoke, Vegetarian, Olives, Onions, Potatoes, Arancini"
		answer = "Our restaurant has several vegetarian options. They are "+ vege_pizzas + "."
		dispatcher.utter_message(text=answer)

		return []
		#return[SlotSet("vege_pizzas", vege_pizzas)]
	
class ActionGetAllPizzas(Action):
	def name(self):
		return 'action_get_all_pizzas'
	
	def run(self, dispatcher, tracker, domain):

		meat_pizzas = "Hawaii, Pepperoni, Ham, Bacon, Mortadella, Salami"
		vege_pizzas = "Funghi, Margherita, Artichoke, Vegetarian, Olives, Onions, Potatoes, Arancini"

		answer = "Our restaurant has many pizzas. They are "+ meat_pizzas + ", " + vege_pizzas + "."
		dispatcher.utter_message(text=answer)

		return []
		#return[SlotSet("vege_pizzas", vege_pizzas), SlotSet("meat_pizzas", meat_pizzas)]
	
class ActionGetPizzaSizes(Action):
	def name(self):
		return 'action_get_sizes'
	
	def run(self, dispatcher, tracker, domain):

		sizes = "small - 10\", medium - 12\", large - 14\", extra large - 18\""

		answer = "We offer these sizes: " + sizes
		dispatcher.utter_message(text=answer)

		return []
	
class ActionGetPizzaCrust(Action):
	def name(self):
		return 'action_get_crust'
	
	def run(self, dispatcher, tracker, domain):

		crusts = "stuffed, cracker, flat bread, thin"

		answer = "We have these crust types: " + crusts
		dispatcher.utter_message(text=answer)

		return []


# for a generic slot validation please refer to https://rasa.com/docs/action-server/validation-action/
class ValidatePizzaOrderForm(FormValidationAction):

	def name(self) -> Text:
		# https://rasa.com/docs/rasa/forms/#advanced-usage
		return "validate_pizza_order_form"

	@staticmethod
	def pizza_db() -> List[Text]:
		"""Database of supported pizzas"""

		return ["hawaii", "funghi", "margherita", "pepperoni", "vegetarian"]
	
	@staticmethod
	def sizes_db() -> List[Text]:
		"""Database of supported sizes"""

		return ["small", "large", "medium", "extra large"]
	
	@staticmethod
	def crust_db() -> List[Text]:
		"""Database of supported crusts"""

		return ["stuffed", "cracker", "thin", "flat bread"]
	
	@staticmethod
	def numbers_db() -> List[Text]:
		"""Database of supported numbers written out"""

		return ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
 				"eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
				"eighteen", "nineteen", "twenty", "twenty one", "twenty two", "twenty three",
				"twenty four", "twenty five", "twenty six", "twenty seven", "twenty eight",
				"twenty nine", "thirty", "thirty one", "thirty two", "thirty three", "thirty four",
				"thirty five", "thirty six", "thirty seven", "thirty eight", "thirty nine", "forty",
				"forty one", "forty two", "forty three", "forty four", "forty five", "forty six",
				"forty seven", "forty eight", "forty nine", "fifty"]

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
			
	def validate_pizza_size(
		self,
		slot_value: Any,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: DomainDict,
	) -> Dict[Text, Any]:
		"""Validate size value."""

		if isinstance(slot_value, str):
			if slot_value.lower() in self.sizes_db():
				# validation succeeded, set the value of the pizza_size slot to value
				return {"pizza_size": slot_value}
			else:
				if any(size_value in slot_value for size_value in ['10', '12', '14', '18']):
					return {"pizza_size": slot_value}
				else:
					return {"pizza_size": None}
		else:
			if any(size_value in slot_value for size_value in [10, 12, 14, 18]):
					return {"pizza_size": slot_value}
			else:
					return {"pizza_size": None}
			
	def validate_pizza_crust(
		self,
		slot_value: Any,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: DomainDict,
	) -> Dict[Text, Any]:
		"""Validate crust value."""

		if isinstance(slot_value, str):
			if slot_value.lower() in self.crust_db():
				# validation succeeded, set the value of the pizza_size slot to value
				return {"pizza_crust": slot_value}
			else:
				return {"pizza_crust": None}
		else:
			return {"pizza_crust": None}
		
	def validate_pizza_amount(
		self,
		slot_value: Any,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: DomainDict,
	) -> Dict[Text, Any]:
		"""Validate amount value."""

		if isinstance(slot_value, str):
			if slot_value.lower() in self.numbers_db():
				# validation succeeded, set the value of the pizza_size slot to value
				return {"pizza_amount": slot_value}
			elif int(slot_value) in range (1,51):
				return {"pizza_amount": slot_value}
			else:
				return {"pizza_amount": None}
		elif isinstance(slot_value, int) and slot_value in range (1,51):
			return {"pizza_amount": slot_value}
		else:
			return {"pizza_amount": None}
		
class ValidateCustomerDetailsForm(FormValidationAction):

	def name(self) -> Text:
		# https://rasa.com/docs/rasa/forms/#advanced-usage
		return "validate_customer_details_form"

	def validate_client_name(
		self,
		slot_value: Any,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: DomainDict,
	) -> Dict[Text, Any]:
		"""Validate name value."""

		if isinstance(slot_value, str):
			return {"client_name": slot_value}
		else:
			return {"client_name": None}
		
	def validate_phone_number(
		self,
		slot_value: Any,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: DomainDict,
	) -> Dict[Text, Any]:
		"""Validate phone value."""

		if isinstance(slot_value, str) and slot_value.isdigit():
			return {"phone_number": slot_value}
		elif isinstance(slot_value, int):
			return {"phone_number": slot_value}
		else:
			return {"phone_number": None}
			