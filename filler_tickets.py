import PIL, time, random
from PIL import Image, ImageDraw, ImageFont, ImageColor

class Filler_tickets:

    def __init__(self, name='Иванов И.И.', departure='Из чата', destination='На х*р!', filename='images/ticket_template.png'):
        self.name = name
        self.departure = departure
        self.destination = destination
        self.filename = filename
        self.create_attr()

    def fill(self):
        ticket = Image.open(self.filename)
        drawer = ImageDraw.Draw(ticket)
        font = ImageFont.truetype('arial.ttf', size=18)
        color = ImageColor.colormap['black']
        drawer.text((50, 120), text=self.name,font=font, embedded_color=True, fill=color)
        drawer.text((50, 190), text=self.departure,font=font, embedded_color=True, fill=color)
        drawer.text((295, 190), text=self.aviaseller, font=font, embedded_color=True, fill=color)
        drawer.text((50, 255), text=self.destination,font=font, embedded_color=True, fill=color)
        drawer.text((285, 255), text=self.date_for_print, font=font, embedded_color=True, fill=color)
        drawer.text((400, 255), text=self.time_for_print, font=font, embedded_color=True, fill=color)
        font = ImageFont.truetype('arial.ttf', size=24)
        drawer.text((45, 320), text=self.plane, font=font, embedded_color=True, fill=color)
        drawer.text((180, 320), text=self.place, font=font, embedded_color=True, fill=color)
        drawer.text((295, 320), text=self.row, font=font, embedded_color=True, fill=color)
        drawer.text((400, 320), text=self.time_for_sit, font=font, embedded_color=True, fill=color)
        ticket.save('images/ticket_for_user.png')
        return ticket  #тикет возвращается только для самотестирования в модуле

    def create_attr(self):
        self.plane = ''
        for i in range(3):
            self.plane = self.plane + chr(random.randint(65,90))
        self.plane = self.plane + ' ' + str(random.randint(1,9)) + str(random.randint(1,9)) + str(random.randint(1,9))
        place = random.randint(1,32)
        self.place = str(place) + str(random.choice(['A','B','C','D']))
        self.row = str(1 + place // 4)
        self.aviaseller = '***** AIRLINES'
        time_now = time.gmtime(time.time() - time.timezone + 60)
        self.date_for_print = time.strftime('%d.%m', time_now)
        self.time_for_print = time.strftime('%H:%M', time_now)
        time_now = time.gmtime(time.time() - time.timezone)
        self.time_for_sit = time.strftime('%H:%M', time_now)


if __name__ == '__main__':
    x = Filler_tickets(name='Баитов Миша')
    ticket = x.fill()
    ticket.show()
