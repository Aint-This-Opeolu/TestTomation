from behave import given, when, then


@given("two numbers 2 and 3")
def step_given_numbers(context):
    context.a = 2
    context.b = 3


@when("I add them")
def step_when_add(context):
    context.result = context.a + context.b


@then("the result should be 5")
def step_then_result(context):
    assert context.result == 5

