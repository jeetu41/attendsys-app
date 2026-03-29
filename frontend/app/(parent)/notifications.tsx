import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import Constants from 'expo-constants';
import { getAuthHeader } from '../../src/store/authStore';
import { useBrandingStore } from '../../src/store/brandingStore';
import { format } from 'date-fns';

const API_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || 'http://localhost:8001';

interface Notification {
  _id: string;
  title: string;
  message: string;
  type: string;
  read: boolean;
  created_at: string;
}

export default function ParentNotificationsScreen() {
  const { branding } = useBrandingStore();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      const headers = await getAuthHeader();
      const response = await axios.get(`${API_URL}/api/notifications`, { headers });
      setNotifications(response.data);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    }
  };

  const markAsRead = async (notificationId: string) => {
    try {
      const headers = await getAuthHeader();
      await axios.post(`${API_URL}/api/notifications/${notificationId}/read`, {}, { headers });
      loadNotifications();
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadNotifications();
    setRefreshing(false);
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'absence': return 'alert-circle';
      case 'homework': return 'book';
      case 'complaint': return 'chatbubble';
      default: return 'notifications';
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'absence': return '#ef4444';
      case 'homework': return branding.primary_color;
      case 'complaint': return '#f59e0b';
      default: return '#64748b';
    }
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {notifications.length === 0 ? (
        <View style={styles.emptyState}>
          <Ionicons name="notifications-outline" size={64} color="#cbd5e1" />
          <Text style={styles.emptyText}>No notifications</Text>
        </View>
      ) : (
        <View style={styles.content}>
          {notifications.map((notif) => (
            <TouchableOpacity
              key={notif._id}
              style={[
                styles.notificationCard,
                !notif.read && styles.notificationUnread,
              ]}
              onPress={() => markAsRead(notif._id)}
            >
              <View
                style={[
                  styles.iconContainer,
                  { backgroundColor: getNotificationColor(notif.type) + '20' },
                ]}
              >
                <Ionicons
                  name={getNotificationIcon(notif.type) as any}
                  size={24}
                  color={getNotificationColor(notif.type)}
                />
              </View>

              <View style={styles.notificationContent}>
                <Text style={styles.notificationTitle}>{notif.title}</Text>
                <Text style={styles.notificationMessage}>{notif.message}</Text>
                <Text style={styles.notificationTime}>
                  {format(new Date(notif.created_at), 'MMM dd, yyyy • h:mm a')}
                </Text>
              </View>

              {!notif.read && <View style={styles.unreadDot} />}
            </TouchableOpacity>
          ))}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  content: {
    padding: 16,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 64,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#64748b',
    marginTop: 16,
  },
  notificationCard: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    alignItems: 'flex-start',
  },
  notificationUnread: {
    backgroundColor: '#f8fafc',
    borderColor: '#cbd5e1',
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  notificationContent: {
    flex: 1,
  },
  notificationTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 4,
  },
  notificationMessage: {
    fontSize: 14,
    color: '#64748b',
    lineHeight: 20,
    marginBottom: 8,
  },
  notificationTime: {
    fontSize: 12,
    color: '#94a3b8',
  },
  unreadDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#6366f1',
    marginLeft: 8,
    marginTop: 8,
  },
});
