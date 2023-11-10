from rest_framework import serializers

from studies.models import Course, Lesson, Payment, Subscription
from studies.validators import LinkValidator
from users.models import User


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'


class SubscriptionListSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='email', queryset=User.objects.all())
    course = serializers.SlugRelatedField(slug_field='title', queryset=Course.objects.all())

    class Meta:
        model = Subscription
        fields = ('id', 'user', 'course')


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('title',)


class LessonListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('title',)


class CourseDetailSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonListSerializer(many=True, read_only=True)
    course_subscription = serializers.SerializerMethodField()

    def get_course_subscription(self, obj):
        return Subscription.objects.filter(course=obj, user=self.context['request'].user).exists()

    def get_lessons_count(self, obj):
        return Lesson.objects.all().filter(course=obj).count()

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('owner', 'lessons_count', 'course_subscription')


class LessonSerializer(serializers.ModelSerializer):
    course = serializers.SlugRelatedField(slug_field='title', queryset=Course.objects.all())
    validators = [LinkValidator(link='link')]

    class Meta:
        model = Lesson
        fields = ('id', 'title', 'description', 'image', 'link', 'course')


class PaymentSerializer(serializers.ModelSerializer):
    payment_method = serializers.SerializerMethodField()

    def get_payment_method(self, obj):
        if obj.payment_method == '1':
            return "Наличные"
        elif obj.payment_method == '2':
            return "Безнал"

    class Meta:
        model = Payment
        fields = ('id', 'user', 'course', 'payment_date', 'payment_method', 'session', 'is_successful')


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('course', 'payment_method')
