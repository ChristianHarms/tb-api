
    <table class="table table-condensed table-striped  table-hover">
        <thead class="table-striped ">
        <tr><th width="30%">Ortname</th><th width="30%">lat/long</th>
            <th width="10%">home</th><th width="10%">Büro</th><th width="10%">Löschen!</th>
            </tr>
        </thead>
        <tbody>
        <form action="/configloc" method="POST">
            {% for location in locations %}
            <tr><td>{{ location.name }}</td>
                <input type="hidden" name="name_{{location.name}}">
                <td>{{ location.pos.lat }}/{{ location.pos.long }}</td>
                <td class="text-center">
                    <input type="checkbox" {{location.home and 'checked'}} name="home_{{ location.name }}">
                </td>
                <td class="text-center">
                    <input type="checkbox" {{location.work and 'checked'}} name="work_{{ location.name }}">
                </td>
                <td class="text-center">
                    <input type="checkbox" name="delete_{{ location.name }}">
                </td>
            </tr>
            {% endfor %}
            <tr><td colspan="5" class="text-right"><input type="submit" value="Speichern"></td></tr>
        </form>
        </tbody>
    </table>