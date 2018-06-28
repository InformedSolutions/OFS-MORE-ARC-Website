def initial_data_filler(form, model, pk, saver=False):
    field_names = [field.name for field in model._meta.get_fields()]
    model_instance = model.objects.get(pk=pk)

    for name, value in form.fields.items():
        if name in field_names:
            form.fields[name].initial = getattr(model_instance, name)


def data_saver(form, model ,pk):
    field_names = [field.name for field in model._meta.get_fields()]
    model_instance = model.objects.get(pk=pk)

    for name, value in form.cleaned_data.items():
        if name in field_names:
            setattr(model_instance, name, value)

    model_instance.save()
