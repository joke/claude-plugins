package com.github.joke.training.order

import spock.lang.Specification
import spock.lang.Subject

@Subject(BadCustomerException)
class BadCustomerExceptionTest extends Specification {

	def 'no-arg constructor creates exception with null message and cause'() {
		final exception = new BadCustomerException()

		expect:
		exception.message == null
		exception.cause == null
	}

	def 'message-only constructor sets message'() {
		final message = 'Invalid customer'
		final exception = new BadCustomerException(message)

		expect:
		exception.message == message
		exception.cause == null
	}

	def 'cause-only constructor sets cause'() {
		final cause = new RuntimeException('Root cause')
		final exception = new BadCustomerException(cause)

		expect:
		exception.cause == cause
		exception.message != null
	}

	def 'message and cause constructor sets both'() {
		final message = 'Invalid customer'
		final cause = new RuntimeException('Root cause')
		final exception = new BadCustomerException(message, cause)

		expect:
		exception.message == message
		exception.cause == cause
	}
}
