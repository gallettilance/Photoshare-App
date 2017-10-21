# CS660_Project1

For best template rendering please execute in Google Chrome

To view the diagram, please go to https://www.draw.io/#Hgalletti94%2FCS660_Project1%2Fmaster%2Fdatabase%2FCS660_ERmodel_Project1.xml


@app.route('/search', methods=['GET', 'POST'])
def search():

   results = []

   if request.method == 'POST':
       search_word = request.form['search_word'];

       query = 'select first_name, user_id_count from users join ' \
               '    (select S.user_id as user_id, count(S.user_id) as user_id_count from ' \
               '    (select user_id from comments where content = %s) S ' \
               '    group by user_id) S1 ' \
               'on S1.user_id = users.user_id'
       cursor.execute(query, search_word)
       for item in cursor:
           results.append(item)

       sorted(results, key=lambda x: x[1])

       return render_template('search.html', search_results=results)

   return render_template('search.html', search_results = results)


@app.route('/friends', methods=['GET', 'POST'])
def friends():
   return render_template('friends.html', name=session.get('email', None).split('@')[0])

@app.route('/friend_delete', methods=['GET', 'POST'])
def friend_delete():
   return render_template('friend_delete.html', name=session.get('email', None).split('@')[0])


@app.route('/people_search', methods=['GET', 'POST'])
def people_search():
   return render_template('people_search.html')
   
   
   
  =====================================================================================================================================================
  the following is the HTML file: search.html
  =================================================================================================================================
  <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='style.css') }}">

<title> search </title>

<body>

<h1 class='profile_header' style="top:0"> search for anything here </h1>




<div class='wrapper'>
    <form class='search_form' action="{{ url_for('search') }}" method=POST>
        input search contain:

        <input type=text name=search_word value="{{request.form.search_word}}" required maxlength=25 placeholder="input your search contain here">
        <input type="submit" value="search">
    </form>
</div>


#render search results
<ul>
    {% if not search_result %}
        {%  for result in search_results %}
            <li> {{ result[0] }}</li>
         {% endfor %}
    {% else %}
          <li> Sorry, no matching result! Try a new search! </li>   #in testing, this line does not show--I don't know why..
    {%  endif %}

</ul>

</body>
