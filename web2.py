import hug
import displayprovider

display = displayprovider.get_display()

@hug.post(output=hug.output_format.json)
def page(data: hug.types.text, response):
    "Show the data on the display. Input data is a text string of 0's and 1's"

    x, y = 0, 0
    for d in data:
        if d == '1':
            onoff = True
        elif d == '0':
            onoff = False
        else:
            response.status = hug.HTTP_400
            return {'message': 'only 1s and 0s allowed'}

        if 0 <= x < display.width and 0 <= y < display.height:
            display.px(x, y, onoff)
        else:
            response.status = hug.HTTP_400
            return {'message': 'image too big'}

        if x+1 < display.width:
            x += 1
        else:
            y += 1
            x = 0

    display.show()

    return {'message': 'ok'}

def test_page():
    import web2
    resp = hug.test.post(web2, 'page', {'data':'110110'})
    assert resp.status == hug.HTTP_200

    resp = hug.test.post(web2, 'page', {'data':'123'})
    assert resp.status == hug.HTTP_400
