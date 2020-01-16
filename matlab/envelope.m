function [up,down] = envelope(x,y,interMethod)
    extrMaxValue = y(find(diff(sign(diff(y)))==-2)+1);
    extrMaxIndex = find(diff(sign(diff(y)))==-2)+1;
    
    extrMinValue = y(find(diff(sign(diff(y)))==2)+1);
    extrMinIndex = find(diff(sign(diff(y)))==2)+1;
    
    up = extrMaxValue;
    up_x = x(extrMaxIndex);
    
    down = extrMinValue;
    down_x = x(extrMinIndex);
    
    up = interp1(up_x, up, x, interMethod);
    down = interp1(down_x, down, x, interMethod);
end

