default = """
{% for metric_name, metric in metrics.items() %}
    # HELP {{ metric_name }} {{ metric['Description'] }}
    # TYPE {{ metric_name }} {{ metric['Type'] }}
    {{ metric_name }} {{ metric['Value'] }}
{% endfor %}
"""
