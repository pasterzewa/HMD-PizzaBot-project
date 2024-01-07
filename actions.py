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

def CalculatePrice(full_order, promotion): # full_order - list, promotion - string
	cost = 0
	margherita_count = 0
	large_count = 0
	print("calculating price")
	for order in full_order:
		# pizza_amount - multiplies the cost for that pizza
		amount_multipier = w2n.word_to_num(order.split()[0])
		# pizza_size - multiplies 0.8, 1, 1.2, 1.5 based on size
		size_multiplier = 1
		if '10\"' in order:
			size_multiplier = 0.8
		elif '12\"' in order:
			size_multiplier = 1
		elif '14\"' in order:
			size_multiplier = 1.2
		elif '18\"' in order:
			size_multiplier = 1.5
		# pizza_crust - stuffed adds 2 euros, flat bread and cracker add 1, thin is the default so it doesn't add anything
		crust_bonus = 0
		if 'stuffed' in order.lower():
			crust_bonus = 2
		elif 'flat bread' in order.lower() or 'cracker' in order.lower():
			crust_bonus = 1
		# pizza_type - Margherita is only 7 euros and that's the base for all pizzas
		# if it's some pizza with one word (Hawaiian, Pepperoni, etc.) then we treat it as a 'normal' pizza with ingredients and it's 10 euros
		# a special pizza adds 2 euros per ingredient
		type_cost = 7
		if "special" in order.lower():
			count_and = order.lower().count(' and ')
			count_comma = order.lower().count(',')
			count_space = order.lower().count(' ')
			count = count_and + count_comma
			if count == 0:
				count = count_space # special case when client was too lazy for punctuation and proper grammar
			type_cost += 2*count
		elif 'margherita' not in order.lower():
			type_cost = 10

		if promotion == "2 Margheritas For The Price of 1" and 'margherita' in order.lower():
			margherita_count += 1
			if margherita_count != 2:
				cost += (type_cost + crust_bonus)*size_multiplier*amount_multipier
			else:
				margherita_count = 0 # this pizza is free and we 'reset' the counter
		elif promotion == "XL Pizza + Small Pepperoni Pizza For Half-Price" and "10\"" in order.lower() and "pepperoni" in order.lower():
			cost += 0.5 * (type_cost + crust_bonus)*size_multiplier*amount_multipier # we add the small pepp for half price
		elif promotion == "2 Large Pizzas and 1 Free":
			large_count += 1
			if large_count != 3:
				cost += (type_cost + crust_bonus)*size_multiplier*amount_multipier
			else:
				large_count = 0 # like with margheritas
		else:
			cost += (type_cost + crust_bonus)*size_multiplier*amount_multipier

	return round(cost, 2)

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
		print("adding pizza")
		pizza_size = tracker.get_slot("pizza_size")
		pizza_type = tracker.get_slot("pizza_type")
		pizza_amount = tracker.get_slot("pizza_amount")
		pizza_crust = tracker.get_slot("pizza_crust")
		pizza_sliced = tracker.get_slot("pizza_sliced")
		promotion = tracker.get_slot("applied_promotion")
		margherita_count = 0
		large_count = 0
		if pizza_size is None:
			pizza_size = "standard"
		sliced = ""
		if pizza_sliced: # must test it!
			sliced = "sliced"
		else:
			sliced = "not sliced"
		order_details =  str(pizza_amount + " "+pizza_type + " of size "+pizza_size + " on " + pizza_crust + " crust, " + sliced)
		old_order = tracker.get_slot("total_order")
		if not isinstance (old_order, list):
			full_order = [order_details]
		else:
			full_order = old_order[0].split('&') + [order_details]

		cost = CalculatePrice (full_order, promotion)

		return[SlotSet("total_order", [order_details]) if old_order is None else SlotSet("total_order", [old_order[0]+' & '+order_details]),
		 		SlotSet("order_cost", cost)]

class ActionResetPizzaForm(Action):
	def name(self):
		return 'action_reset_pizza_form'

	def run(self, dispatcher, tracker, domain):
		print("resetting form")
		return[SlotSet("pizza_type", None),SlotSet("pizza_size", None),SlotSet("pizza_amount", None),SlotSet("pizza_crust", None),SlotSet("pizza_sliced", None)]
	
class ActionResetEverything(Action):
	def name(self):
		return 'action_reset_everything'

	def run(self, dispatcher, tracker, domain):
		print("resetting everything")
		return[SlotSet("pizza_type", None),SlotSet("pizza_size", None),SlotSet("pizza_amount", None),SlotSet("pizza_crust", None),SlotSet("pizza_sliced", None),
		 SlotSet("total_order", None),SlotSet("order_cost", None),SlotSet("client_name", None),SlotSet("phone_number", None),SlotSet("delivery_address", None),
		 SlotSet("applied_promotion", None),SlotSet("possible_promotion", None),SlotSet("possible_promotion_conditions_met", None)]

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
		print("checking promotion")
		order = tracker.get_slot("total_order")[0]
		order_split = order.split('&')
		ok = False
		if promotion == "2 Large Pizzas and 1 Free":
			count_of_14_inch = 0 # calculate the amount of ordered large pizzas
			for ord in order_split:
				amount = w2n.word_to_num(ord.split()[0]) # first word is the amount
				if "14\"" in ord:
					count_of_14_inch += amount 
				if count_of_14_inch >= 3:
					ok = True 
					break
		elif promotion == "2 Margheritas For The Price of 1":
			margherita_count = 0
			for ord in order_split:
				amount = w2n.word_to_num(ord.split()[0])
				if "margherita" in ord.lower():
					margherita_count += amount 
				if margherita_count >= 2:
					ok = True 
					break
		elif promotion == "XL Pizza + Small Pepperoni Pizza For Half-Price":
			xl_present = False
			pepp_present = False
			for ord in order_split:
				if "18\"" in ord.lower():
					xl_present = True 
				elif "10\"" in ord.lower() and "pepperoni" in ord.lower():
					pepp_present = True
				if xl_present and pepp_present:
					ok = True 
					break
		else:
			print("wrong promotion")

		if ok:
			order = tracker.get_slot("total_order")
			full_order = order[0].split('&')
			cost = CalculatePrice(full_order, promotion)
			return[SlotSet("applied_promotion", promotion), SlotSet("order_cost", cost)]
		else:
			return[SlotSet("possible_promotion", None)]
	
class ActionSuggestPromotion(Action):
	def name(self):
		return 'action_suggest_promotion'

	def run(self, dispatcher, tracker, domain):
		print("looking for promotions")
		order = tracker.get_slot("total_order")[0]
		order_split = order.split('&')
		promotion = None
		ok = False
		conditions_met = False
		count_of_14_inch = 0
		margherita_count = 0
		xl_present = False
		pepp_present = False

		for ord in order_split:
			amount = w2n.word_to_num(ord.split()[0]) # first word is the amount
			if "14\"" in ord:
				count_of_14_inch += amount
			if "margherita" in ord.lower():
				margherita_count += amount 
			if "18\"" in ord.lower():
				xl_present = True 
			elif "10\"" in ord.lower() and "pepperoni" in ord.lower():
				pepp_present = True		

		# "2 Large Pizzas and 1 Free"
		# check if the user has at least two large pizzas
		# if 3 already - set the possible_promotion_conditions_met to True
				
		# "2 Margheritas For The Price of 1"
		# check if the user has at least one margherita
		# if 2 already - set the possible_promotion_conditions_met to True

		# "XL Pizza + Small Pepperoni Pizza For Half-Price":
		# check if the client has either pizza in size 18" or a small pepperoni
		# if both already - set the possible_promotion_conditions_met to True

		if count_of_14_inch >= 3:
			promotion = "2+1 Large Pizzas"
			ok = True
			conditions_met = True 
		elif margherita_count >= 2:
			promotion = "2 Margheritas For The Price of 1"
			ok = True
			conditions_met = True 
		elif xl_present and pepp_present:
			promotion = "XL Pizza + Small Pepperoni Pizza For Half-Price"
			ok = True
			conditions_met = True 

		if ok == False:
			if count_of_14_inch == 2:
				promotion = "2+1 Large Pizzas"
				ok = True
			elif margherita_count == 1:
				promotion = "2 Margheritas For The Price of 1"
				ok = True
			elif xl_present or pepp_present:
				promotion = "XL Pizza + Small Pepperoni Pizza For Half-Price"
				ok = True

		if ok:
			return[SlotSet("possible_promotion", promotion), SlotSet("possible_promotion_conditions_met", conditions_met)]
		else:
			return[]

class ActionApplyPromotion(Action):
	def name(self):
		return 'action_apply_promotion'
	
	def run(self, dispatcher, tracker, domain):
		print("applying promotion")
		promotion = tracker.get_slot("applied_promotion")
		order = tracker.get_slot("total_order")
		full_order = order[0].split('&')
		cost = CalculatePrice (full_order, promotion)
		return[SlotSet("applied_promotion", tracker.get_slot("possible_promotion")), SlotSet("order_cost", cost)]

class ActionGetRestaurantLocation(Action):
	def name(self):
		return 'action_get_restaurant_location'

	def run(self, dispatcher, tracker, domain):
		print("setting restaurant location")
		restaurant_address = "Via Giuseppe Verdi, 15, 38122 Trento TN"
		answer = "Our restaurant is located at " + restaurant_address
		dispatcher.utter_message(text=answer)

		return[SlotSet("restaurant_location", restaurant_address)]

class ActionGetMeatPizzas(Action):
	def name(self):
		return 'action_get_meat_pizzas'
	
	def run(self, dispatcher, tracker, domain):
		print("meat pizzas")
		meat_pizzas = "Hawaii, Pepperoni, Ham, Bacon, Mortadella, Salami"
		answer = "Our restaurant has several meat options. They are "+ meat_pizzas + "."
		dispatcher.utter_message(text=answer)

		return []
		#return[SlotSet("meat_pizzas", meat_pizzas)]

class ActionGetVegePizzas(Action):
	def name(self):
		return 'action_get_vege_pizzas'
	
	def run(self, dispatcher, tracker, domain):
		print("vege pizzas")
		vege_pizzas = "Funghi, Margherita, Artichoke, Vegetarian, Olives, Onions, Potatoes, Arancini"
		answer = "Our restaurant has several vegetarian options. They are "+ vege_pizzas + "."
		dispatcher.utter_message(text=answer)

		return []
		#return[SlotSet("vege_pizzas", vege_pizzas)]
	
class ActionGetAllPizzas(Action):
	def name(self):
		return 'action_get_all_pizzas'
	
	def run(self, dispatcher, tracker, domain):
		print("all pizzas")
		meat_pizzas = "Hawaii, Pepperoni, Ham, Bacon, Mortadella, Salami"
		vege_pizzas = "Funghi, Margherita, Artichoke, Vegetarian, Olives, Onions, Potatoes, Arancini, Tomatoes"

		answer = "Our restaurant has many pizzas. They are "+ meat_pizzas + ", " + vege_pizzas + "."
		dispatcher.utter_message(text=answer)

		return []
		#return[SlotSet("vege_pizzas", vege_pizzas), SlotSet("meat_pizzas", meat_pizzas)]
	
class ActionGetPizzaSizes(Action):
	def name(self):
		return 'action_get_sizes'
	
	def run(self, dispatcher, tracker, domain):
		print("sizes")
		sizes = "small - 10\", medium - 12\", large - 14\", extra large - 18\""

		answer = "We offer these sizes: " + sizes
		dispatcher.utter_message(text=answer)

		return []
	
class ActionGetPizzaCrust(Action):
	def name(self):
		return 'action_get_crust'
	
	def run(self, dispatcher, tracker, domain):
		print("crust")
		crusts = "stuffed, cracker, flat bread, thin"

		answer = "We have these crust types: " + crusts
		dispatcher.utter_message(text=answer)

		return []
	
class ActionGetPromotions(Action):
	def name(self):
		return 'action_get_promotions'
	
	def run(self, dispatcher, tracker, domain):
		print("get promo")
		promo = "2 Large Pizzas and 1 Free, 2 Margheritas For The Price of 1, XL Pizza + Small Pepperoni Pizza For Half-Price"

		answer = "We are currently running following promotions: " + promo
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
			