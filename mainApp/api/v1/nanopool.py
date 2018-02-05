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


class SaveWorkerStats(APIView):
    """
    Saves stats for given worker. Takes pool address and worker id
    """
    permission_classes =  (AllowAny,)

    def post(self, request):

        pool = request.data['pool']
        worker = request.data['workerID']
        worker_stats = request.data['worker_stats']

        pool_obj = PoolModel.objects.get(address=pool)
        if pool_obj:
            worker_obj = WorkerModel.objects.get(pool=pool_obj, nano_id=worker)
            if worker_obj:
                new_stats = WorkerStats.objects.get_or_create(
                    worker=worker_obj,
                    last_share = datetime.datetime.fromtimestamp(worker_stats['lastshare']),
                    hashrate = float(worker_stats['hashrate']),
                    avg_h1 = float(worker_stats['h1']),
                    avg_h3 = float(worker_stats['h3']),
                    avg_h6 =float(worker_stats['h6']),
                    avg_h12 = float(worker_stats['h12']),
                    avg_h24 = float(worker_stats['h24'])
                )
                return Response(create_response_scelet(u"success", u"data saved", {}), status.HTTP_200_OK)
            else:
                return Response(create_response_scelet(u"failure", u"Worket with such id not found", {}), status.HTTP_200_OK)
        else:
            return Response(create_response_scelet(u"failure", u"Pool with provided address wasn't found", {} ), status.HTTP_200_OK)









