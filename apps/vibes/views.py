from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from .serializers import CreateVibeSerializer, VibeHistorySerializer
from rest_framework.views import APIView
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from .models import Vibe

class CreateVibeView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = CreateVibeSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            vibe = serializer.save()

            return Response({
                "status": True,
                "message": "Vibe created successfully",
                "data": {
                    "id":           vibe.id,
                    "mood_bucket":  vibe.mood_bucket,
                    "mood_slider":  vibe.mood_slider,
                    "mood_text":    vibe.mood_text,
                    "latitude":     float(vibe.latitude),
                    "longitude":    float(vibe.longitude),
                    "address":      vibe.address,
                    "timer_seconds":vibe.timer_seconds,
                    "end_time":     vibe.end_time.isoformat(),
                    "is_active":    vibe.is_active,
                    "status":       vibe.status
                }
            }, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            # ---- collect missing‑field names ---------------------------------
            missing = [
                field
                for field, msgs in e.detail.items()
                if (isinstance(msgs, (list, tuple)) and msgs and msgs[0] == "This field is required.")
                or msgs == "This field is required."
            ]

            if missing:
                # join with comma and add grammar
                sentence = ", ".join(missing) + (" field is required." if len(missing) == 1
                                                else " fields are required.")
            else:
                # fallback – join all error strings
                flat = [
                    f"{field}: {' '.join(msgs) if isinstance(msgs, (list, tuple)) else msgs}"
                    for field, msgs in e.detail.items()
                ]
                sentence = " | ".join(flat)
            return Response({
                "status": False,
                "message": "Validation Error",
                "errors": sentence
            }, status=400)

        except IntegrityError as e:
            return Response({
                "status": False,
                "message": "Database Error",
                "errors": str(e)
            }, status=400)

        except Exception as e:
            return Response({
                "status": False,
                "message": "Unexpected Error",
                "errors": str(e)
            }, status=500)

class VibeHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            vibes = Vibe.objects.filter(user=user)

            # ── Optional filters ──────────────────────
            status_param      = request.query_params.get('status')
            is_active_param   = request.query_params.get('is_active')
            mood_bucket_param = request.query_params.get('mood_bucket')
            start_after       = request.query_params.get('start_after')
            end_before        = request.query_params.get('end_before')

            if status_param:
                vibes = vibes.filter(status=status_param)

            if is_active_param in ['true', 'false']:
                vibes = vibes.filter(is_active=(is_active_param.lower() == 'true'))

            if mood_bucket_param:
                vibes = vibes.filter(mood_bucket=mood_bucket_param)

            if start_after:
                dt = parse_datetime(start_after)
                if dt:
                    vibes = vibes.filter(start_time__gte=dt)

            if end_before:
                dt = parse_datetime(end_before)
                if dt:
                    vibes = vibes.filter(end_time__lte=dt)

            vibes = vibes.order_by('-created_at')

            serializer = VibeHistorySerializer(vibes, many=True)
            return Response({
                "status": True,
                "message": "Vibe history fetched successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({
                "status": False,
                "message": "Validation Error",
                "errors": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError as e:
            return Response({
                "status": False,
                "message": "Database Error",
                "errors": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": False,
                "message": "Unexpected Error",
                "errors": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)