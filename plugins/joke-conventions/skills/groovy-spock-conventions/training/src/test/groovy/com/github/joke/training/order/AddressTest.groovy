package com.github.joke.training.order

import groovy.transform.CompileStatic
import spock.lang.Specification
import spock.lang.Subject

@CompileStatic
class AddressTest extends Specification {

    @Subject
    Address address = new Address('123 Main St', 'Springfield', 'IL', '62701', 'US')

    def "returns full address formatted with all fields"() {
        when:
        String result = address.fullAddress

        then:
        result == '123 Main St, Springfield, IL 62701, US'
        0 * _
    }

    def "addresses with same fields are equal"() {
        Address other = new Address('123 Main St', 'Springfield', 'IL', '62701', 'US')

        expect:
        address == other
    }

    def "addresses with different fields are not equal"() {
        Address other = new Address('456 Elm St', 'Springfield', 'IL', '62701', 'US')

        expect:
        address != other
    }

    def "returns full address for each combination of fields"() {
        Address addr = new Address(street, city, state, zipCode, country)

        expect:
        addr.fullAddress == expected

        where:
        street        | city          | state | zipCode | country || expected
        '1 A St'      | 'Chicago'     | 'IL'  | '60601' | 'US'    || '1 A St, Chicago, IL 60601, US'
        '99 Oak Ave'  | 'Los Angeles' | 'CA'  | '90001' | 'US'    || '99 Oak Ave, Los Angeles, CA 90001, US'
        '7 Rue Neuve' | 'Paris'       | 'IDF' | '75001' | 'FR'    || '7 Rue Neuve, Paris, IDF 75001, FR'
    }

}
