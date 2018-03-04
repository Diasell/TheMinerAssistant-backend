# -*- coding: utf-8 -*-
#  import django services
import datetime
from django.contrib.auth.models import User


# import rest framework services
from rest_framework.authtoken.models import Token
from rest_framework.authentication import (
    TokenAuthentication,
    BasicAuthentication)
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView


# import needed app models
from mainApp.models.userProfile import UserProfileModel
from mainApp.models.worker import (
    WorkerModel,
    WorkerStats,
    PoolModel
)

# import helper functions
from mainApp.utils.helperfunctions import (
    validate_user_registration,
    create_response_scelet
)

class GetPools(APIView):
    """
    view for NanoPool Script to get the list of all pools to track
    """
    permission_classes = (AllowAny,)

    def get(self, request):
        list_of_pools = [pool.address for pool in PoolModel.objects.all()]
        if list_of_pools:
            response = create_response_scelet(u"success", u"success", list_of_pools)
        else:
            response = create_response_scelet(u"failure", u"no pools available",  [])

        return Response(response, status.HTTP_200_OK)


class SavePoolStats(APIView):
    """
    Saves stats for given workers. Takes pool address
    """
    permission_classes =  (AllowAny,)

    def post(self, request):

        pool_id = request.data['account']
        workers_array= request.data['workers']

        pool = PoolModel.objects.get(address=pool_id)
        if pool:
            pool.hashrate = float(request.data['hashrate'])
            pool.avg_hasrate = float(request.data['avgHashrate']['h1'])
            pool.balance = float(request.data['balance'])
            pool.unconfirmed_balance = float(request.data['unconfirmed_balance'])
            pool.save()

            if workers_array:
                for worker in workers_array:
                    worker_obj = WorkerModel.objects.get_or_create(pool=pool, worker_name=worker['id'])[0]
                    stats, created = WorkerStats.objects.get_or_create(worker=worker_obj, last_share=datetime.datetime.fromtimestamp(worker['lastshare']))

                    if created:
                            stats.hashrate=float(worker['hashrate'])
                            stats.avg_h1=float(worker['h1'])
                            stats.avg_h3=float(worker['h3'])
                            stats.avg_h6=float(worker['h6'])
                            stats.avg_h12=float(worker['h12'])
                            stats.avg_h24=float(worker['h24'])
                            stats.save()
                    else:
                        continue
                return Response(create_response_scelet(u"success", u"data saved", {}), status.HTTP_200_OK)
        else:
            return Response(create_response_scelet(u"failure", u"Pool with provided address wasn't found", {} ), status.HTTP_404_NOT_FOUND)









