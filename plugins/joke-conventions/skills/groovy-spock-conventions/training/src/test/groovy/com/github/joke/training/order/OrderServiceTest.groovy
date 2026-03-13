package com.github.joke.training.order

import groovy.transform.CompileStatic
import org.apache.commons.collections4.ListUtils
import spock.lang.Specification
import spock.lang.Subject

@CompileStatic
class OrderServiceTest extends Specification {

    CustomerRepository customerRepository = Mock()

    @Subject(OrderService)
    final orderService = Spy(new OrderService(customerRepository))

    def 'add customer delegates to repository'() {
        Customer customer = Mock()

        when:
        orderService.addCustomer(customer)

        then:
        1 * customerRepository.saveCustomer(customer)
        1 * orderService.addCustomer(customer)
        0 * _
    }

    def 'get customers returns unmodifiable list from repository'() {
        SpyStatic(ListUtils)

        List<Customer> customers = Mock()
        List<Customer> unmodifiableCustomers = Mock()

        when:
        final List<Customer> result = orderService.customers

        then:
        1 * customerRepository.customers >> customers
        1 * ListUtils.unmodifiableList(customers) >> unmodifiableCustomers
        1 * orderService.customers
        0 * _

        expect:
        result.is(unmodifiableCustomers)
    }

    def 'find customer by prefix returns first matching customer'() {
        Customer customer1 = Mock()
        Customer customer2 = Mock()

        when:
        final Optional<Customer> result = orderService.findCustomerByPrefix('some')

        then:
        1 * customerRepository.customers >> [customer1, customer2]
        1 * orderService.isCustomerWithMatchingName('some', customer1) >> true
        1 * orderService.findCustomerByPrefix('some')
        0 * _

        expect:
        !result.empty
        result.get().is(customer1)
    }

    def 'find customer by prefix returns empty when no customer matches'() {
        Customer customer1 = Mock()
        Customer customer2 = Mock()

        when:
        final Optional<Customer> result = orderService.findCustomerByPrefix('some')

        then:
        1 * customerRepository.customers >> [customer1, customer2]
        1 * orderService.isCustomerWithMatchingName('some', customer1) >> false
        1 * orderService.isCustomerWithMatchingName('some', customer2) >> false
        1 * orderService.findCustomerByPrefix('some')
        0 * _

        expect:
        result.empty
    }

    def 'is customer with matching name returns true when name starts with customer name'() {
        Customer customer = Mock()

        when:
        final boolean result = orderService.isCustomerWithMatchingName('Johnathan', customer)

        then:
        1 * customer.name >> 'John'
        1 * orderService.isCustomerWithMatchingName('Johnathan', customer)
        0 * _

        expect:
        result
    }

    def 'is customer with matching name returns false when name does not start with customer name'() {
        Customer customer = Mock()

        when:
        final boolean result = orderService.isCustomerWithMatchingName('Jane', customer)

        then:
        1 * customer.name >> 'John'
        1 * orderService.isCustomerWithMatchingName('Jane', customer)
        0 * _

        expect:
        !result
    }

    def 'isBadCustomer throws BadCustomerException'() {
        when:
        orderService.isBadCustomer()

        then:
        1 * orderService.isBadCustomer()
        0 * _

        final BadCustomerException ex = thrown()

        expect:
        ex.message == 'Bad customer'
    }
}
