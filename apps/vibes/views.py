from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError

from .serializers import CreateVibeSerializer

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
                    "timer_seconds": vibe.timer_seconds,
                    "end_time":     vibe.end_time.isoformat(),
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
