import { ComponentFixture, TestBed } from '@angular/core/testing';
import { WrksNavigationComponent } from './wrks-navigation.component';

describe('WrksNavigationComponent', () => {
  let component: WrksNavigationComponent;
  let fixture: ComponentFixture<WrksNavigationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WrksNavigationComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(WrksNavigationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
