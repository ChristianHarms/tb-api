
<h2>Orte bestimmen</h2>
  {% if devices %}
    <table class="table table-condensed table-striped  table-hover">
        <thead class="table-striped ">
        <tr><th>Ortname</th><th>lat/long</th><th>home</th><th>Büro</th></tr>
        </thead>
        <tbody>
        <form action="/config" method="POST">
            {% for location in locations %}
            <tr><td>{{ location.name }}</td>
                <td>{{ location.pos.lat }}/{{ location.pos.lng }}</td>
                <td class="text-center"><input type="checkbox" {{location.home and 'checked'}}
                    name="home_{{ location.name }}"></td>
                <td class="text-center"><input type="checkbox" {{location.work and 'checked'}}
                    name="work{{ location.name }}"></td>
                <td class="text-center"><input type="checkbox"
                                               name="delete_{{ location.name }}"></td>
            </tr>
            {% endfor %}
            <tr><td colspan="4" class="text-right"><input type="submit" value="Speichern"></td></tr>
        </form>
        </tbody>
    </table>
  {% else %}
    <div class="alert alert-danger" role="alert">
        Es sind keine Orte gespeichert.
        {% if geofency.length>0 %} Willst du Orte aus den letzten geofency Daten übernehmen?
        {% endif %}
    </div>

  {% endif %}