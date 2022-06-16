package org.ligi.fast.model;

import android.util.Log;

import java.util.Comparator;
import java.util.Locale;

class AppInfoSortByPinComparator implements Comparator<AppInfo> {

    @Override
    public int compare(AppInfo lhs, AppInfo rhs) {
        if (lhs.getPinMode() == rhs.getPinMode()) {
            return 0;
        }
        else if (lhs.getPinMode() < rhs.getPinMode()) {
            return 1;
        }
        else {
            return -1;
        }
    }

}
