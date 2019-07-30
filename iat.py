import xlrd
import re

class Row():

	def __init__(self, name, init_load, html):
		self.name = name
		self.init_load = init_load
		self.html = html

	def calc_base_name(self):
		#snake case Name field
		self.name = self.name.lower()
		self.name = self.name.replace(" ", "_")

	def calc_prefix(self):
		if '<input type="text"' in self.html:
			self.prefix = "txt"
			return
		if '<input type="submit"' in self.html or '<button' in self.html:
			self.prefix = "btn"
			return
		if '<select' in self.html:
			self.prefix = "lb"
			return
		if '<span' in self.html:
			self.prefix = "span"
			return
		self.prefix = "***" #default to be manually overwritten

	def calc_suffix(self):
		split_html = self.html.split()
		for unit in split_html:
			if "id=" in unit:
				self.suffix = "id"
				self.arg = unit[len('id="'):][:-1]
				return
		for unit in split_html:
			if "name=" in unit:
				self.suffix = "name"
				self.arg = unit[len('name="'):][:-1]
				return
		self.suffix = "xpath"
		self.arg = "***"


	def calc(self):
		self.calc_base_name()
		self.calc_prefix()
		self.calc_suffix()
		self.full_name = self.prefix + "_" + self.name + "_" + self.suffix + " = " + '"' + self.arg + '"'
		return self.full_name


path = "page_data.xlsx"
input_wb = xlrd.open_workbook(path)

f = open("output.txt", "w")

for sheet in input_wb.sheets():
	all_rows = []
	for y in range(1, sheet.nrows):
		row = Row(sheet.cell_value(y, 0), sheet.cell_value(y, 1), sheet.cell_value(y, 2))
		all_rows.append(row)
	f.write("###PAGE CLASS###\n")
	f.write("class " + sheet.name.replace(" ", "") + "Page():\n")
	for element in all_rows:
		f.write("\t" + element.calc() + "\n")

	f.write("\n")
	f.write("\tdef __init__(self, browser):\n")
	f.write("\t\tself.waiter = WaitUntil(browser.driver, browser.wait)\n")
	f.write('\t\tself.waiter.element_is_visible("' + all_rows[0].suffix + '", self.' + all_rows[0].prefix + "_" + all_rows[0].name + "_" + all_rows[0].suffix +')\n')
	f.write("\n")
	f.write("\t\tself.locator = Locator(browser.driver)\n")
	for element in all_rows:
		f.write("\t\tself." + element.prefix + "_" + element.name + 
			' = self.locator.get_element("' + element.suffix + 
			'", self.' + element.prefix + "_" + element.name + "_" + element.suffix + ")\n")


	x = re.sub( r"([A-Z])", r" \1", sheet.name)	
	x = x.lstrip()
	x = x.rstrip()
	x = x.replace("  ", "_")
	x = x.lower()
	page_obj = x + "_page"
	f.write("\n")
	f.write("###FILL OUT FUNCTION###\n")
	f.write("def " + x + "(browser):\n")
	f.write("\t" + page_obj + " = pages_iedss." + sheet.name.replace(' ', '') + "Page(browser)\n")
	f.write("\n")
	for element in all_rows:
		if element.prefix == "txt":
			f.write("\t#interact.send_text(" + page_obj + "." + element.prefix + "_" + element.name + ", ***)\n")
			continue
		if element.prefix == "btn" or element.prefix == "span":
			f.write("\t#interact.click_element(" + page_obj + "." + element.prefix + "_" + element.name + ")\n")
			continue
		if element.prefix == "lb":
			f.write("\t#interact.select_item_from_listbox(" + page_obj + "." + element.prefix + "_" + element.name + ", ***)\n")
			continue
		f.write("\t#interact.***(" + page_obj + "." + element.prefix + "_" + element.name + ", ***)\n")
	f.write("\n")
	f.write("###FUNCTION CALL###\n")
	f.write("fill_out_iedss." + x + "(browser)\n\n\n")
f.close()
