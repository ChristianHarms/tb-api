{% if devices %}
<h2>Gerätekonfiguration</h2>
<table class="table table-condensed table-striped  table-hover">
    <thead class="table-striped ">
    <tr><th width="35%">Geräte-ID</th><th width="35%">Name</th><th width="15%">Blockiert?</th><th width="15%">Löschen!</th></tr>
    </thead>
    <tbody>
    <form action="/configdev" method="POST">
        {% for device in devices %}
        <tr><td>{{ device.device_id }}</td>
            <td><input id="{{ device.device_id }}" name="name_{{ device.device_id }}"
                       placeHolder="Name" size=15 value="{{device.name}}"></td>
            <td class="text-center"><input type="checkbox" {{device.blocked and 'checked'}}
                name="block_{{ device.device_id }}"></td>
            <td class="text-center"><input type="checkbox"
                                           name="delete_{{ device.device_id }}"></td>
        </tr>
        {% endfor %}
        <tr><td colspan="4" class="text-right"><input type="submit" value="Speichern"></td></tr>
    </form>
    </tbody>
</table>
{% else %}
{% endif %}
