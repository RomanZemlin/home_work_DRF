from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework import viewsets, generics, serializers
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from studies.models import Course, Lesson, Payment, Subscription
from studies.paginators import Paginator
from studies.permissions import IsNotStaffUser, IsOwnerOrStaffUser
from studies.serializers import LessonSerializer, CourseDetailSerializer, SubscriptionSerializer, \
    SubscriptionListSerializer, PaymentCreateSerializer, PaymentSerializer
from studies.services import subscriptions_update_course_mailing, subscriptions_lesson_mailing, \
    subscriptions_create_lesson_mailing, get_session, retrieve_session


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseDetailSerializer
    queryset = Course.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrStaffUser]
    pagination_class = Paginator

    def get_queryset(self):
        if not self.request.user.is_staff:
            return Course.objects.filter(owner=self.request.user)
        elif self.request.user.is_staff:
            return Course.objects.all()
        else:
            raise PermissionDenied

    def create(self, request, *args, **kwargs):
        if request.user.is_staff:
            raise PermissionDenied
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.is_staff:
            raise PermissionDenied
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)
        subscriptions_update_course_mailing(serializer)


class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsNotStaffUser]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        subscriptions_create_lesson_mailing(serializer)


class LessonListAPIView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    pagination_class = Paginator

    def get_queryset(self):
        if not self.request.user.is_staff:
            return Lesson.objects.filter(owner=self.request.user)
        elif self.request.user.is_staff:
            return Lesson.objects.all()
        else:
            raise PermissionDenied


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsOwnerOrStaffUser]


class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsOwnerOrStaffUser]

    def perform_update(self, serializer):
        subscriptions_lesson_mailing(serializer)
        serializer.save()


class LessonDestroyAPIView(generics.DestroyAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsNotStaffUser]


class SubscriptionCreateAPIView(generics.CreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsNotStaffUser]

    def create(self, request, *args, **kwargs):
        for subscription in Subscription.objects.filter(user=self.request.user):
            if subscription.course.id == request.data.get('course'):
                raise PermissionDenied('У вас уже есть подписка на этот курс.')
        if self.request.user.id != request.data.get('user'):
            raise PermissionDenied('Нельзя оформлять подписки на другого пользователя.')
        return super().create(request, *args, **kwargs)


class SubscriptionListAPIView(generics.ListAPIView):
    serializer_class = SubscriptionListSerializer

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


class SubscriptionDestroyAPIView(generics.DestroyAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsNotStaffUser]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


class PaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ('course', 'payment_method')
    ordering_fields = ('payment_date',)

    def get_queryset(self):
        if not self.request.user.is_staff:
            return Payment.objects.filter(user=self.request.user)
        elif self.request.user.is_staff:
            return Payment.objects.all()
        else:
            raise PermissionDenied


class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentCreateSerializer

    def perform_create(self, serializer):
        course = serializer.validated_data.get('course')
        if not course:
            raise serializers.ValidationError('Не указан курс.')
        payment = serializer.save()
        payment.user = self.request.user
        if payment.payment_method == '2':
            payment.session = get_session(payment).id
        payment.save()


class PaymentRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        if obj.session:
            session = retrieve_session(obj.session)
            if session.payment_status == 'paid' and session.status == 'complete':
                obj.is_successful = True
                obj.save()
        self.check_object_permissions(self.request, obj)
        return obj


class PaymentDestroyAPIView(generics.DestroyAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsNotStaffUser]
