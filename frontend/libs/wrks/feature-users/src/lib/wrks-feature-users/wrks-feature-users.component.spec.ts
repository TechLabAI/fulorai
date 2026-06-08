import { ComponentFixture, TestBed } from '@angular/core/testing';
import { WrksFeatureUsersComponent } from './wrks-feature-users.component';

describe('WrksFeatureUsersComponent', () => {
  let component: WrksFeatureUsersComponent;
  let fixture: ComponentFixture<WrksFeatureUsersComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WrksFeatureUsersComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(WrksFeatureUsersComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
