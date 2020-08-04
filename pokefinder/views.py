from django.shortcuts import render
from . import services


def main(request):
  poke_id = 443
  df = services.get_df(poke_id)
  data = services.get_data(df)
  context = {'data': data}
  return render(request, 'main.html', context)
