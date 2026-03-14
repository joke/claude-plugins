package com.github.joke.training.order

import spock.lang.Specification
import spock.lang.Subject

@Subject(Address)
class AddressTest extends Specification {

	def 'constructor initializes all fields correctly'() {
		final address = new Address('123 Main St', 'Springfield', 'IL', '62701', 'USA')

		expect:
		verifyAll(address) {
			street == '123 Main St'
			city == 'Springfield'
			state == 'IL'
			zipCode == '62701'
			country == 'USA'
		}
	}

	def 'getFullAddress handles various address formats'() {
		final address = new Address(street, city, state, zipCode, country)

		expect:
		address.fullAddress == expectedFormat

		where:
		street           | city          | state | zipCode | country   || expectedFormat
		'123 Main St'    | 'Springfield' | 'IL'  | '62701' | 'USA'     || '123 Main St, Springfield, IL 62701, USA'
		'456 Oak Ave'    | 'Chicago'     | 'IL'  | '60601' | 'USA'     || '456 Oak Ave, Chicago, IL 60601, USA'
		'789 Elm Road'   | 'Toronto'     | 'ON'  | 'M5V3A9'| 'Canada'  || '789 Elm Road, Toronto, ON M5V3A9, Canada'
	}
}
