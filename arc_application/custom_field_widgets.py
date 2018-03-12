from django.forms import widgets


class Widget(widgets.Widget):
    input_classes = 'form-control'
    input_error_classes = 'form-control-error'

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        css_classes = self.input_classes() if callable(self.input_classes) else self.input_classes
        attrs['class'] = ('%s %s' % (attrs.get('class', ''), css_classes)).strip()
        return attrs


class CustomCheckboxInput(widgets.CheckboxInput, Widget):
    template_name = 'widgets/checkbox.html'
    inherit_label_from_field = True
    label = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conditionally_revealed = {}

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if self.label:
            context['widget']['label'] = self.label
        context['conditionally_revealed'] = self.conditionally_revealed.get(True)
        return context


class Textarea(widgets.Textarea, Widget):
    def __init__(self, attrs=None):
        default_attrs = {'cols': '40', 'rows': '3'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__()
