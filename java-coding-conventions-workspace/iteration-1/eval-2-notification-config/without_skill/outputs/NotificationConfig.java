package com.example.config;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class NotificationConfig {

    private final String defaultChannel;
    private final List<String> enabledChannels;
    private final Map<String, String> channelSettings;
    private final boolean retryEnabled;
    private final int maxRetries;

    public NotificationConfig(final String defaultChannel,
                              final List<String> enabledChannels,
                              final Map<String, String> channelSettings,
                              final boolean retryEnabled,
                              final int maxRetries) {
        this.defaultChannel = defaultChannel;
        this.enabledChannels = Collections.unmodifiableList(new ArrayList<>(enabledChannels));
        this.channelSettings = Collections.unmodifiableMap(new HashMap<>(channelSettings));
        this.retryEnabled = retryEnabled;
        this.maxRetries = maxRetries;
    }

    public String getDefaultChannel() {
        return defaultChannel;
    }

    public List<String> getEnabledChannels() {
        return enabledChannels;
    }

    public Map<String, String> getChannelSettings() {
        return channelSettings;
    }

    public boolean isRetryEnabled() {
        return retryEnabled;
    }

    public int getMaxRetries() {
        return maxRetries;
    }

    public boolean isChannelEnabled(final String channel) {
        return enabledChannels.contains(channel);
    }
}
