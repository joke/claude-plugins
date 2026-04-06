package com.example.config;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class NotificationConfig {

    private String defaultChannel;
    private List<String> enabledChannels;
    private Map<String, String> channelSettings;
    private boolean retryEnabled;
    private int maxRetries;

    public NotificationConfig() {
        this.enabledChannels = new ArrayList<>();
        this.channelSettings = new HashMap<>();
        this.retryEnabled = false;
        this.maxRetries = 3;
    }

    public String getDefaultChannel() {
        return defaultChannel;
    }

    public void setDefaultChannel(String defaultChannel) {
        this.defaultChannel = defaultChannel;
    }

    public List<String> getEnabledChannels() {
        return enabledChannels;
    }

    public void setEnabledChannels(List<String> enabledChannels) {
        this.enabledChannels = enabledChannels;
    }

    public void addChannel(String channel) {
        enabledChannels.add(channel);
    }

    public void removeChannel(String channel) {
        enabledChannels.remove(channel);
    }

    public Map<String, String> getChannelSettings() {
        return channelSettings;
    }

    public void setChannelSettings(Map<String, String> channelSettings) {
        this.channelSettings = channelSettings;
    }

    public void putSetting(String key, String value) {
        channelSettings.put(key, value);
    }

    public boolean isRetryEnabled() {
        return retryEnabled;
    }

    public void setRetryEnabled(boolean retryEnabled) {
        this.retryEnabled = retryEnabled;
    }

    public int getMaxRetries() {
        return maxRetries;
    }

    public void setMaxRetries(int maxRetries) {
        this.maxRetries = maxRetries;
    }

    public boolean isChannelEnabled(String channel) {
        for (String c : enabledChannels) {
            if (c.equals(channel)) {
                return true;
            }
        }
        return false;
    }
}
