from io import BytesIO

from fpdf import FPDF


FONT = 'DejaVuSans'


class JsonToPdf(FPDF):
    """Класс для формирования вывода в PDF."""

    def __init__(self):
        """Настройка фона."""
        super().__init__()
        self.add_font(FONT,
                      '',
                      f'fonts/{FONT}-Bold.ttf',
                      uni=1)

    def header(self):
        """Настройка шапки."""
        self.set_font(FONT, '', 12)
        self.multi_cell(0, 10,
                        txt='Список покупок:',
                        border=0, align='C', ln=1
                        )
        self.ln(20)

    def footer(self):
        """Настройка подвала."""
        self.set_y(-25)
        self.set_font(FONT, '', 10)
        self.cell(30, 10, 'Foodgram. Inc.', ln=1)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def json_transformer(self, final_ingredients: dict):
        """Логика преобразования в PDF."""
        self.add_page()
        self.set_font(FONT, '', 10)
        self.set_auto_page_break(auto=1, margin=20)
        self.multi_cell(0, 10,
                        f'Список покупок для рецептов '
                        f'{", ".join(final_ingredients.keys())}.',
                        ln=1
                        )
        self.ln()
        self.cell(0, 10,
                  'Вам понадобится:',
                  ln=1
                  )
        self.ln()
        all_ingredients = []
        same_ingredients = {}
        for ingredients_list in final_ingredients.values():
            all_ingredients.extend(ingredients_list)
        for ingredient in all_ingredients:
            ingredient_name = ingredient['ingredient_name']
            ingredient_quantity = ingredient['ingredient_quantity']
            measurement_unit = ingredient['measurement_unit']
            if ingredient_name in same_ingredients:
                same_ingredients[ingredient_name]['ingredient_quantity'] += \
                    ingredient_quantity
            else:
                same_ingredients[ingredient_name] = {
                    "ingredient_quantity": ingredient_quantity,
                    "measurement_unit": measurement_unit
                }
        for ingredient_name, ingredient_data in same_ingredients.items():
            ingredient_info = (
                f'{ingredient_name} '
                f'в количестве {ingredient_data["ingredient_quantity"]} '
                f'{ingredient_data["measurement_unit"]}'
            )
            lines = self.cell(0, 10, ingredient_info)
            if isinstance(lines, list):
                for line in lines:
                    self.cell(0, 10, txt=line, ln=True)
            else:
                self.cell(0, 10, txt=lines, ln=True)
        pdf_bytes = BytesIO()
        self.output(pdf_bytes)
        return pdf_bytes.getvalue()
