package com.github.joke.training.order

import org.apache.commons.lang3.Validate
import spock.lang.Specification
import spock.lang.Subject

import static com.github.joke.training.order.CustomerType.PREMIUM
import static com.github.joke.training.order.CustomerType.STANDARD
import static com.github.joke.training.order.CustomerType.VIP

@Subject(Customer)
class CustomerTest extends Specification {

    def 'creates customer with required id and null optional fields'() {
        final customer = new Customer('CUST-001')

        expect:
        verifyAll(customer) {
            id == 'CUST-001'
            name == null
            email == null
            address == null
            type == null
        }
    }

    def 'setName validates and assigns name'() {
        SpyStatic(Validate)

        final customer = new Customer('CUST-001')

        when:
        customer.name = 'Alice'

        then:
        1 * Validate.notBlank('Alice')
        0 * _

        expect:
        customer.name == 'Alice'
    }

    def 'setName rejects blank name'() {
        SpyStatic(Validate)

        final customer = new Customer('CUST-001')

        when:
        customer.name = ''

        then:
        thrown(IllegalArgumentException)
        0 * _
    }

    def 'isPremium returns expected result for customer type'() {
        final customer = new Customer('CUST-001').with(true) {
            type = customerType
        }
        final result = customer.premium

        expect:
        result == expectedPremium

        where:
        customerType || expectedPremium
        VIP          || true
        PREMIUM      || true
        STANDARD     || false
    }
}
