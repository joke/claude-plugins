package com.github.joke.training.order

import groovy.transform.CompileStatic
import spock.lang.Specification
import spock.lang.Subject

@CompileStatic
class BadCustomerExceptionTest extends Specification {

    @Subject
    BadCustomerException exception

    def 'is a RuntimeException'() {
        exception = new BadCustomerException()

        expect:
        exception instanceof RuntimeException
    }

    def 'constructed with no args has null message and null cause'() {
        exception = new BadCustomerException()

        expect:
        verifyAll(exception) {
            message == null
            cause == null
        }
    }

    def 'constructed with message carries the message'() {
        exception = new BadCustomerException('bad customer')

        expect:
        exception.message == 'bad customer'
    }

    def 'constructed with cause carries the cause'() {
        RuntimeException cause = new RuntimeException('root cause')
        exception = new BadCustomerException(cause)

        expect:
        verifyAll(exception) {
            exception.cause.is(cause)
            message == cause.toString()
        }
    }

    def 'constructed with message and cause carries both'() {
        RuntimeException cause = new RuntimeException('root cause')
        exception = new BadCustomerException('bad customer', cause)

        expect:
        verifyAll(exception) {
            message == 'bad customer'
            exception.cause.is(cause)
        }
    }
}
