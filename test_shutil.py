import re

# points_regex = re.compile(r'(Points available: )(\d+)')
# html_bout = "<br>Points available: 1254<h3>Competitions:</h3><ul>"
# mo = points_regex.search(html_bout)
test_comp = "Spring Festival"

# start_str = "Fall Classic"
# end_str = 
places_regex = \
            re.compile(f'({test_comp}.*?Places: )(\\d+)', re.DOTALL)
response_html = """<li>
            Spring Festival<br />
            Date: 2020-03-27 10:00:00</br>
            Number of Places: 24
            
            <a href="/book/Spring%20Festival/Simply%20Lift">Book Places</a>
            
        </li>
        <hr />
        
        <li>
            Fall Classic<br />
            Date: 2020-10-22 13:30:00</br>
            Number of Places: 13
            """
mo = places_regex.search(response_html)
# print(mo)
# print(mo.group())
# print(mo.group(0))
# print(mo.group(1))
print(mo.group(2))