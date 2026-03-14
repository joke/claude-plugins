package com.github.joke.training.order

import org.apache.commons.lang3.Validate
import spock.lang.Specification
import spock.lang.Subject

import static com.github.joke.training.order.CustomerType.*

@Subject(Customer)
class CustomerTest extends Specification {

    def 'creates customer with required id'() {
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

    def 'set address'() {
        SpyStatic(Validate)

        final customer = new Customer('CUST-001')

        when:
        customer.name = 'some-name'

        then:
        1 * Validate.notBlank('some-name')
        1 * Validate.notBlank(*_)
        0 * _

        expect:
        customer.name == 'some-name'
    }

    def 'is premium'() {
        final customer = new Customer('CUST-001').with(true) {
            type = premiumType
        }
        final res = customer.premium

        expect:
        res == isPremium

        where:
        premiumType || isPremium
        VIP         || true
        PREMIUM     || true
        STANDARD    || false
    }
}
