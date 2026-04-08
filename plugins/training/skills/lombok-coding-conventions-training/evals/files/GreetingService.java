package com.example.greeting;

import javax.inject.Inject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class GreetingService {

    private static final Logger logger = LoggerFactory.getLogger(GreetingService.class);

    private final GreetingRepository repository;
    private final Translator translator;

    @Inject
    GreetingService(final GreetingRepository repository, final Translator translator) {
        this.repository = repository;
        this.translator = translator;
    }

    public String greet(final String userId, final String locale) {
        logger.info("Greeting user {} in {}", userId, locale);
        final String template = repository.findTemplate(userId);
        return translator.translate(template, locale);
    }
}
